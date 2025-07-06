from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class VulnerabilityType(Enum):
    """Types of security vulnerabilities"""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    AUTHENTICATION_BYPASS = "auth_bypass"
    AUTHORIZATION_BYPASS = "authz_bypass"
    DATA_EXPOSURE = "data_exposure"
    INPUT_VALIDATION = "input_validation"
    CHILD_PRIVACY = "child_privacy"
    PARENTAL_CONTROL_BYPASS = "parental_bypass"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SESSION_HIJACKING = "session_hijacking"


class Severity(Enum):
    """Vulnerability severity levels"""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class SecurityVulnerability:
    """Represents a discovered security vulnerability"""

    vulnerability_type: VulnerabilityType
    severity: Severity
    description: str
    affected_function: str
    payload: str
    response: str
    remediation: str
    child_safety_impact: bool
    exploit_code: Optional[str] = None
    references: List[str] = None


@dataclass
class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[str]


class SecurityTestResult:
    """Result from security testing"""

    test_name: str
    vulnerabilities: List[SecurityVulnerability]
    execution_time: float
    tests_run: int
    passed_tests: int
    failed_tests: int
    coverage_areas: List[
