import asyncio
import logging
from typing import Any, Callable, Dict

from .models import SecurityVulnerability, Severity, VulnerabilityType
from .payloads import (auth_bypass_payloads, command_injection_payloads,
                       data_exposure_payloads, path_traversal_payloads,
                       sql_injection_payloads, validation_payloads, xss_payloads)

logger = logging.getLogger(__name__)


async def _execute_test(target_function, payload, context):
    """Execute a single security test"""
    if asyncio.iscoroutinefunction(target_function):
        return await target_function(payload, context)
    else:
        return target_function(payload, context)


def _indicates_sql_injection(response) -> bool:
    """Check for SQL injection indicators"""
    if not response:
        return False

    response_text = str(response).lower()
    sql_indicators = [
        "sql syntax",
        "mysql",
        "postgres",
        "database error",
        "table",
        "column",
        "select",
        "union",
        "drop table",
    ]

    return any(indicator in response_text for indicator in sql_indicators)


def _contains_xss_reflection(response, payload) -> bool:
    """Check if XSS payload was reflected"""
    if not response:
        return False

    response_text = str(response)
    # Check if script tags or javascript: are present
    return (
        "<script>" in response_text
        or "javascript:" in response_text
        or "onerror=" in response_text
        or "onload=" in response_text
    )


def _indicates_command_execution(response) -> bool:
    """Check for command execution indicators"""
    if not response:
        return False

    response_text = str(response).lower()
    command_indicators = [
        "root:",
        "uid=",
        "gid=",
        "/bin/",
        "/usr/bin/",
        "command not found",
        "permission denied",
        "directory listing",
    ]

    return any(
        indicator in response_text for indicator in command_indicators)


def _indicates_file_access(response) -> bool:
    """Check for file system access indicators"""
    if not response:
        return False

    response_text = str(response).lower()
    file_indicators = [
        "etc/passwd",
        "system32",
        "file not found",
        "directory",
        "permission denied",
        "appdata",
    ]

    return any(indicator in response_text for indicator in file_indicators)


def _indicates_auth_bypass(response) -> bool:
    """Check for authentication bypass indicators"""
    if not response:
        return False

    response_text = str(response).lower()
    auth_indicators = [
        "admin access",
        "authenticated",
        "logged in",
        "access granted",
        "welcome admin",
        "authorization success",
    ]

    return any(indicator in response_text for indicator in auth_indicators)


def _indicates_data_exposure(response) -> bool:
    """Check for data exposure indicators"""
    if not response:
        return False

    response_text = str(response).lower()
    data_indicators = [
        "user data:",
        "child_id:",
        "password:",
        "token:",
        "database dump",
        "user list",
        "confidential",
    ]

    return any(indicator in response_text for indicator in data_indicators)


def _indicates_validation_bypass(response, payload) -> bool:
    """Check for input validation bypass"""
    if not response:
        return False

    # Check if very long payload was processed without truncation
    if len(payload) > 1000 and len(str(response)) > 500:
        return True

    # Check if null bytes were processed
    if "\x00" in payload and str(response):
        return True

    return False


async def test_sql_injection(
    target_function, child_context
) -> Dict[str, Any]:
    """Test SQL injection vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in sql_injection_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for SQL injection indicators
            if _indicates_sql_injection(response):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.SQL_INJECTION,
                    severity=Severity.CRITICAL,
                    description=f"Potential SQL injection vulnerability with payload: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Use parameterized queries and input validation",
                    child_safety_impact=True,
                    references=["OWASP SQL Injection Prevention"],
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            # Database errors might indicate SQL injection
            if "sql" in str(e).lower() or "database" in str(e).lower():
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.SQL_INJECTION,
                    severity=Severity.HIGH,
                    description=f"Database error suggests SQL injection: {str(e)}",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(e),
                    remediation="Implement proper error handling and input validation",
                    child_safety_impact=True,
                )
                vulnerabilities.append(vulnerability)
            failed += 1

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_xss_vulnerabilities(
    target_function, child_context
) -> Dict[str, Any]:
    """Test XSS vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in xss_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check if XSS payload was reflected
            if _contains_xss_reflection(response, payload):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.XSS,
                    severity=Severity.HIGH,
                    description=f"XSS vulnerability detected with payload: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Implement output encoding and content security policy",
                    child_safety_impact=True,
                    references=["OWASP XSS Prevention"],
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            failed += 1
            logger.error(f"XSS test failed: {e}")

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_command_injection(
    target_function, child_context
) -> Dict[str, Any]:
    """Test command injection vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in command_injection_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for command execution indicators
            if _indicates_command_execution(response):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                    severity=Severity.CRITICAL,
                    description=f"Command injection detected: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Avoid system command execution, use safe APIs",
                    child_safety_impact=True,
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            failed += 1
            logger.error(f"Command injection test failed: {e}")

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_path_traversal(
    target_function, child_context
) -> Dict[str, Any]:
    """Test path traversal vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in path_traversal_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for file system access
            if _indicates_file_access(response):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.PATH_TRAVERSAL,
                    severity=Severity.HIGH,
                    description=f"Path traversal vulnerability: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Validate and sanitize file paths, use whitelist approach",
                    child_safety_impact=True,
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            failed += 1
            logger.error(f"Path traversal test failed: {e}")

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_authentication_bypass(
    target_function, child_context
) -> Dict[str, Any]:
    """Test authentication bypass vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in auth_bypass_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for authentication bypass
            if _indicates_auth_bypass(response):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.AUTHENTICATION_BYPASS,
                    severity=Severity.CRITICAL,
                    description=f"Authentication bypass possible: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Implement strong authentication and session management",
                    child_safety_impact=True,
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            failed += 1
            logger.error(f"Authentication test failed: {e}")

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_data_exposure(
    target_function, child_context
) -> Dict[str, Any]:
    """Test data exposure vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in data_exposure_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for data exposure
            if _indicates_data_exposure(response):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                    severity=Severity.HIGH,
                    description=f"Data exposure detected: '{payload}'",
                    affected_function=target_function.__name__,
                    payload=payload,
                    response=str(response)[:200],
                    remediation="Implement proper access controls and data filtering",
                    child_safety_impact=True,
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            failed += 1
            logger.error(f"Data exposure test failed: {e}")

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }


async def test_input_validation(
    target_function, child_context
) -> Dict[str, Any]:
    """Test input validation vulnerabilities"""
    vulnerabilities = []
    tests_run = 0
    passed = 0
    failed = 0

    for payload in validation_payloads:
        tests_run += 1

        try:
            response = await _execute_test(
                target_function, payload, child_context
            )

            # Check for validation bypass
            if _indicates_validation_bypass(response, payload):
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                    severity=Severity.MEDIUM,
                    description=f"Input validation bypass: '{payload[:50]}...'",
                    affected_function=target_function.__name__,
                    payload=payload[:100],
                    response=str(response)[:200],
                    remediation="Implement comprehensive input validation and sanitization",
                    child_safety_impact=False,
                )
                vulnerabilities.append(vulnerability)
                failed += 1
            else:
                passed += 1

        except Exception as e:
            # Check if exception indicates vulnerability
            if "buffer" in str(e).lower() or "overflow" in str(e).lower():
                vulnerability = SecurityVulnerability(
                    vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                    severity=Severity.HIGH,
                    description=f"Input validation error: {str(e)}",
                    affected_function=target_function.__name__,
                    payload=payload[:100],
                    response=str(e),
                    remediation="Implement proper error handling and input validation",
                    child_safety_impact=False,
                )
                vulnerabilities.append(vulnerability)
            failed += 1

    return {
        "vulnerabilities": vulnerabilities,
        "tests_run": tests_run,
        "passed": passed,
        "failed": failed,
    }
