"""
Advanced threat detection engine for the security manager.
"""
import logging
import re
from ipaddress import ip_address, ip_network
from typing import Any, Dict, List, Optional, Tuple

from .models import ThreatLevel

logger = logging.getLogger(__name__)


class ThreatDetectionEngine:
    """
    Analyzes requests for potential threats, including injection attacks,
    suspicious patterns, and IP reputation issues.
    """

    def __init__(self):
        self.suspicious_patterns = [
            re.compile(p, re.IGNORECASE) for p in [
                r"(union\s+select|drop\s+table|--|;)",  # SQLi
                r"(<script|javascript:|onload=|onerror=)",  # XSS
                r"(\.\./|\.\.\\|%2e%2e)",  # Path Traversal
                r"(&&|\|\||;)\s*(ls|cat|rm|whoami)",  # Command Injection
            ]
        ]
        self.suspicious_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp"
        ]
        # In a real app, this would be a dynamic, external feed
        self.ip_blacklist: set[ip_network] = {ip_network("10.0.0.0/8")}
        self.ip_reputation_cache: Dict[str, Dict[str, Any]] = {}

    async def analyze_request(self, request) -> Tuple[ThreatLevel, List[str]]:
        """
        Analyzes an incoming request for a wide range of potential security threats.

        Returns the highest threat level detected and a list of identified threat descriptions.
        """
        threats = []
        max_threat_level = ThreatLevel.LOW

        client_ip = request.client.host if request.client else "unknown"

        # 1. Check IP Reputation
        ip_threat, ip_threat_level = await self._check_ip_reputation(client_ip)
        if ip_threat:
            threats.append(ip_threat)
            max_threat_level = max(max_threat_level, ip_threat_level)

        # 2. Check User Agent
        ua_threat, ua_threat_level = self._check_user_agent(
            request.headers.get("user-agent", ""))
        if ua_threat:
            threats.append(ua_threat)
            max_threat_level = max(max_threat_level, ua_threat_level)

        # 3. Check for Injection Patterns in Query Params and Path
        request_path_and_query = str(request.url)
        if self._check_for_injection(request_path_and_query):
            threats.append("Potential injection pattern detected in URL.")
            max_threat_level = max(max_threat_level, ThreatLevel.HIGH)

        # Note: For a complete solution, the request body should also be inspected for POST/PUT.

        return max_threat_level, threats

    async def _check_ip_reputation(self, ip: str) -> Tuple[Optional[str], ThreatLevel]:
        """Checks IP reputation against a blacklist and other (mocked) threat intel."""
        if not ip or ip == "unknown":
            return None, ThreatLevel.LOW

        try:
            ip_obj = ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback:
                return None, ThreatLevel.LOW

            for blacklisted_net in self.ip_blacklist:
                if ip_obj in blacklisted_net:
                    return f"IP {ip} is in a blacklisted network.", ThreatLevel.CRITICAL
        except ValueError:
            return f"Invalid IP address format: {ip}", ThreatLevel.MEDIUM

        # In a real system, you would query external threat intelligence APIs here.
        return None, ThreatLevel.LOW

    def _check_user_agent(self, user_agent: str) -> Tuple[Optional[str], ThreatLevel]:
        """Checks for suspicious user agents."""
        ua_lower = user_agent.lower()
        for suspicious_ua in self.suspicious_user_agents:
            if suspicious_ua in ua_lower:
                return f"Suspicious user agent detected: {suspicious_ua}", ThreatLevel.MEDIUM
        return None, ThreatLevel.LOW

    def _check_for_injection(self, value: str) -> bool:
        """Checks a string value against all suspicious patterns."""
        return any(pattern.search(value) for pattern in self.suspicious_patterns)
