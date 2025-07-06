"""
Threat detection component for the API Gateway.
"""
import logging
import re
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Set

from .models import ThreatLevel, ThreatSignature

logger = logging.getLogger(__name__)


class ThreatDetectorMixin:
    """A mixin providing threat detection capabilities, including signature matching and DDoS prevention."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threat_signatures: List[ThreatSignature] = self._initialize_threat_signatures(
        )
        self.blocked_ips: Set[str] = set()
        self.whitelisted_ips: Set[str] = set()
        self.ddos_thresholds: Dict[str, int] = {
            'requests_per_minute': 1000,
            'unique_ips_threshold': 50,  # Lowered for more aggressive detection
        }
        self.request_analytics: deque = kwargs.get(
            "request_analytics", deque(maxlen=10000))

    def _initialize_threat_signatures(self) -> List[ThreatSignature]:
        """Initializes a default set of security threat signatures."""
        return [
            ThreatSignature("sql_injection", r"(union\s+select|' or '1'='1|--|;)",
                            ThreatLevel.CRITICAL, "block", "SQL Injection Attempt"),
            ThreatSignature("xss", r"(<script>|javascript:|onerror=)",
                            ThreatLevel.HIGH, "block", "Cross-Site Scripting Attempt"),
            ThreatSignature("command_injection", r"(&&|\|\||;)\s*(ls|cat|rm|whoami)",
                            ThreatLevel.CRITICAL, "block", "Command Injection Attempt"),
            ThreatSignature("path_traversal", r"(\.\./|\.\.\\)",
                            ThreatLevel.HIGH, "block", "Path Traversal Attempt"),
            ThreatSignature("suspicious_ua", r"(sqlmap|nmap|nikto|masscan)",
                            ThreatLevel.MEDIUM, "log", "Suspicious User-Agent"),
        ]

    async def run_security_checks(self, request) -> Dict[str, any]:
        """Runs all security checks for an incoming request."""
        client_ip = self._get_client_ip(request)

        if client_ip in self.blocked_ips:
            return self._build_response(False, 403, "IP address is permanently blocked.")
        if self.whitelisted_ips and client_ip not in self.whitelisted_ips:
            return self._build_response(False, 403, "IP address is not whitelisted.")

        if await self._check_threat_signatures(request):
            # Block IP after a threat is detected
            self.blocked_ips.add(client_ip)
            return self._build_response(False, 403, "Security threat detected and IP blocked.")

        if await self._detect_ddos_attack():
            self.blocked_ips.add(client_ip)  # Block IP on DDoS suspicion
            return self._build_response(False, 429, "Potential DDoS attack detected. Try again later.")

        return {"allowed": True}

    async def _check_threat_signatures(self, request) -> bool:
        """Checks the request against a list of known threat signatures."""
        content_to_check = f"{request.url} {request.headers.get('user-agent', '')}"
        # In a real scenario, you'd also check the request body for POST/PUT requests

        for sig in self.threat_signatures:
            if re.search(sig.pattern, content_to_check, re.IGNORECASE):
                logger.warning("Threat signature matched",
                               signature=sig.name, ip=self._get_client_ip(request))
                if sig.action == "block":
                    return True
        return False

    async def _detect_ddos_attack(self) -> bool:
        """Detects a potential DDoS attack based on request volume and IP diversity."""
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = [
            r for r in self.request_analytics if r.timestamp > one_minute_ago]

        if len(recent_requests) > self.ddos_thresholds['requests_per_minute']:
            unique_ips = len({r.ip_address for r in recent_requests})
            if unique_ips < self.ddos_thresholds['unique_ips_threshold']:
                logger.critical("Potential DDoS attack detected",
                                request_count=len(recent_requests),
                                unique_ips=unique_ips)
                return True
        return False

    def _build_response(self, allowed: bool, status_code: int = 200, message: str = "") -> Dict[str, any]:
        """Helper to build a consistent response dictionary."""
        return {"allowed": allowed, "status_code": status_code, "message": message}

    # Placeholder that the main gateway class will implement
    def _get_client_ip(self, request) -> str: raise NotImplementedError
