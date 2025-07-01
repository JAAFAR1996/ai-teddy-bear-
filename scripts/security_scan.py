import argparse
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List


class SecurityScanner:
    """
    Comprehensive security scanning utility for the AI Teddy Bear project
    """

    def __init__(self):
        """
        Initialize security scanner
        """
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def run_bandit_scan(self, directory: str = "src") -> Dict[str, Any]:
        """
        Run Bandit security scanner for Python code

        :param directory: Directory to scan
        :return: Bandit scan results
        """
        try:
            # Ensure output directory exists
            os.makedirs("security_reports", exist_ok=True)

            # Run Bandit scan
            output_file = "security_reports/bandit_report.json"
            result = subprocess.run(
                ["bandit", "-r", directory, "-f", "json", "-o", output_file],
                capture_output=True,
                text=True,
            )

            # Read and parse Bandit results
            with open(output_file, "r") as f:
                bandit_results = json.load(f)

            return {
                "total_issues": len(bandit_results["results"]),
                "issues_by_severity": self._categorize_bandit_issues(
                    bandit_results["results"]
                ),
            }

        except Exception as e:
            self._logger.error(f"Bandit scan error: {e}")
            return {"error": str(e)}

    def _categorize_bandit_issues(self, issues: List[Dict]) -> Dict[str, int]:
        """
        Categorize Bandit issues by severity

        :param issues: List of Bandit issues
        :return: Categorized issue counts
        """
        severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

        for issue in issues:
            severity = issue.get("issue_severity", "LOW").upper()
            severity_counts[severity] += 1

        return severity_counts

    def run_safety_check(self) -> Dict[str, Any]:
        """
        Check Python dependencies for known security vulnerabilities

        :return: Safety check results
        """
        try:
            # Ensure output directory exists
            os.makedirs("security_reports", exist_ok=True)

            # Run safety check
            output_file = "security_reports/safety_report.json"
            result = subprocess.run(
                [
                    "safety",
                    "check",
                    "--full-report",
                    "--output",
                    "json",
                    "--output-file",
                    output_file,
                ],
                capture_output=True,
                text=True,
            )

            # Read and parse Safety results
            with open(output_file, "r") as f:
                safety_results = json.load(f)

            return {
                "total_vulnerabilities": len(safety_results),
                "vulnerabilities_by_severity": self._categorize_safety_issues(
                    safety_results
                ),
            }

        except Exception as e:
            self._logger.error(f"Safety check error: {e}")
            return {"error": str(e)}

    def _categorize_safety_issues(self, vulnerabilities: List[Dict]) -> Dict[str, int]:
        """
        Categorize safety vulnerabilities by severity

        :param vulnerabilities: List of safety vulnerabilities
        :return: Categorized vulnerability counts
        """
        severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW").upper()
            severity_counts[severity] += 1

        return severity_counts

    def run_trufflehog_scan(self, repository_path: str = ".") -> Dict[str, Any]:
        """
        Scan for secrets and sensitive information

        :param repository_path: Path to repository to scan
        :return: Trufflehog scan results
        """
        try:
            # Ensure output directory exists
            os.makedirs("security_reports", exist_ok=True)

            # Run Trufflehog scan
            output_file = "security_reports/trufflehog_report.json"
            result = subprocess.run(
                [
                    "trufflehog",
                    "filesystem",
                    repository_path,
                    "--json",
                    "--output",
                    output_file,
                ],
                capture_output=True,
                text=True,
            )

            # Read and parse Trufflehog results
            with open(output_file, "r") as f:
                trufflehog_results = json.load(f)

            return {
                "total_secrets_found": len(trufflehog_results),
                "secrets_by_type": self._categorize_trufflehog_secrets(
                    trufflehog_results
                ),
            }

        except Exception as e:
            self._logger.error(f"Trufflehog scan error: {e}")
            return {"error": str(e)}

    def _categorize_trufflehog_secrets(self, secrets: List[Dict]) -> Dict[str, int]:
        """
        Categorize secrets by type

        :param secrets: List of secrets found
        :return: Categorized secret counts
        """
        secret_types = {}

        for secret in secrets:
            secret_type = secret.get("type", "unknown")
            secret_types[secret_type] = secret_types.get(secret_type, 0) + 1

        return secret_types

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report

        :return: Comprehensive security scan results
        """
        report = {
            "timestamp": os.getenv("DEPLOYMENT_TIMESTAMP", "Unknown"),
            "bandit_scan": self.run_bandit_scan(),
            "safety_check": self.run_safety_check(),
            "secret_scan": self.run_trufflehog_scan(),
        }

        # Export report
        self._export_report(report)

        return report

    def _export_report(
        self,
        report: Dict[str, Any],
        output_path: str = "security_reports/comprehensive_report.json",
    ):
        """
        Export security report to JSON

        :param report: Security scan report
        :param output_path: Path to export report
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(report, f, indent=4)

            self._logger.info(
                f"Comprehensive security report exported to {output_path}"
            )
        except Exception as e:
            self._logger.error(f"Error exporting security report: {e}")


def main():
    """
    CLI for security scanning
    """
    parser = argparse.ArgumentParser(description="AI Teddy Bear Security Scanner")
    parser.add_argument(
        "--bandit", action="store_true", help="Run Bandit security scan"
    )
    parser.add_argument(
        "--safety", action="store_true", help="Run Safety dependency check"
    )
    parser.add_argument(
        "--trufflehog", action="store_true", help="Run Trufflehog secret scan"
    )
    parser.add_argument(
        "--comprehensive", action="store_true", help="Run comprehensive security scan"
    )

    args = parser.parse_args()

    scanner = SecurityScanner()

    if args.comprehensive:
        report = scanner.generate_comprehensive_report()
        print(json.dumps(report, indent=4))
    else:
        if args.bandit:
            print(json.dumps(scanner.run_bandit_scan(), indent=4))

        if args.safety:
            print(json.dumps(scanner.run_safety_check(), indent=4))

        if args.trufflehog:
            print(json.dumps(scanner.run_trufflehog_scan(), indent=4))


if __name__ == "__main__":
    main()
