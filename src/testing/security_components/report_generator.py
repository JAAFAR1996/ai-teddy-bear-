import time
from typing import Any, Dict, List

from .models import SecurityTestResult, SecurityVulnerability, Severity, VulnerabilityType


def _aggregate_vulnerabilities(
    vulnerabilities_found: List[SecurityVulnerability],
) -> Dict[str, Any]:
    """Aggregate found vulnerabilities."""
    total_vulnerabilities = len(vulnerabilities_found)
    critical_vulns = len(
        [v for v in vulnerabilities_found if v.severity == Severity.CRITICAL]
    )
    high_vulns = len(
        [v for v in vulnerabilities_found if v.severity == Severity.HIGH]
    )
    child_safety_vulns = len(
        [v for v in vulnerabilities_found if v.child_safety_impact]
    )

    vuln_types = {}
    for vuln in vulnerabilities_found:
        vuln_type = vuln.vulnerability_type.value
        vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1

    return {
        "total_vulnerabilities": total_vulnerabilities,
        "critical_vulnerabilities": critical_vulns,
        "high_vulnerabilities": high_vulns,
        "child_safety_impact": child_safety_vulns,
        "vulnerability_breakdown": vuln_types,
        "security_score": max(0, 100 - (critical_vulns * 20) - (high_vulns * 10)),
    }


def _generate_security_recommendations(
    vulnerabilities_found: List[SecurityVulnerability],
) -> List[str]:
    """Generate security recommendations based on findings"""
    recommendations = []

    vuln_types = set(
        v.vulnerability_type for v in vulnerabilities_found)

    if VulnerabilityType.CHILD_PRIVACY in vuln_types:
        recommendations.append(
            "Implement strict personal information filtering for all child interactions"
        )

    if VulnerabilityType.PARENTAL_CONTROL_BYPASS in vuln_types:
        recommendations.append(
            "Strengthen parental control enforcement and add bypass detection"
        )

    if VulnerabilityType.SQL_INJECTION in vuln_types:
        recommendations.append(
            "Use parameterized queries and implement SQL injection protection"
        )

    if VulnerabilityType.XSS in vuln_types:
        recommendations.append(
            "Implement output encoding and Content Security Policy"
        )

    if VulnerabilityType.INAPPROPRIATE_CONTENT in vuln_types:
        recommendations.append(
            "Enhance content filtering with multi-layer safety checks"
        )

    # General recommendations
    recommendations.extend(
        [
            "Conduct regular security penetration testing",
            "Implement comprehensive logging and monitoring",
            "Establish incident response procedures for child safety violations",
            "Regular security training for development team",
            "Third-party security audit of child safety systems",
        ])

    return recommendations


async def generate_security_report(
    test_results: List[SecurityTestResult],
    vulnerabilities_found: List[SecurityVulnerability],
) -> Dict[str, Any]:
    """Generate comprehensive security report by orchestrating helper methods."""
    if not test_results:
        return {"error": "No test results available"}

    summary_data = _aggregate_vulnerabilities(vulnerabilities_found)
    recommendations = _generate_security_recommendations(vulnerabilities_found)

    return {
        "timestamp": time.time(),
        "summary": summary_data,
        "detailed_vulnerabilities": [
            {
                "type": v.vulnerability_type.value,
                "severity": v.severity.value,
                "description": v.description,
                "function": v.affected_function,
                "payload": v.payload,
                "remediation": v.remediation,
                "child_safety_impact": v.child_safety_impact,
            }
            for v in vulnerabilities_found
        ],
        "recommendations": recommendations,
        "test_coverage": [result.coverage_areas for result in test_results],
    }
