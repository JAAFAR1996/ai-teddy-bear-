import json
import logging
import os
import platform
import socket
import subprocess
import sys
from typing import Any, Dict

import psutil


class SystemDiagnostics:
    """
    Comprehensive system diagnostics and health check utility
    """

    def __init__(self):
        """
        Initialize system diagnostics
        """
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_system_info(self) -> Dict[str, Any]:
        """
        Collect comprehensive system information

        :return: Dictionary of system details
        """
        try:
            return {
                "os": {
                    "platform": platform.platform(),
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "compiler": platform.python_compiler(),
                    "build_date": platform.python_build()[1],
                },
                "hardware": {
                    "cpu_count": os.cpu_count(),
                    "memory": {
                        "total": psutil.virtual_memory().total / (1024**3),  # GB
                        "available": psutil.virtual_memory().available / (1024**3),
                        "percent_used": psutil.virtual_memory().percent,
                    },
                    "disk": {
                        "total": psutil.disk_usage("/").total / (1024**3),
                        "free": psutil.disk_usage("/").free / (1024**3),
                        "percent_used": psutil.disk_usage("/").percent,
                    },
                },
                "network": {
                    "hostname": socket.gethostname(),
                    "ip_address": socket.gethostbyname(socket.gethostname()),
                },
            }
        except Exception as e:
            self._logger.error(f"Error collecting system information: {e}")
            return {}

    def check_ai_dependencies(self) -> Dict[str, Any]:
        """
        Check AI and ML dependencies

        :return: Dictionary of dependency status
        """
        dependencies = [
            "openai",
            "elevenlabs",
            "torch",
            "transformers",
            "whisper",
            "redis",
            "sqlalchemy",
        ]

        dependency_status = {}

        for dep in dependencies:
            try:
                module = __import__(dep)
                dependency_status[dep] = {
                    "installed": True,
                    "version": module.__version__,
                }
            except (ImportError, AttributeError):
                dependency_status[dep] = {"installed": False, "version": None}

        return dependency_status

    def gpu_diagnostics(self) -> Dict[str, Any]:
        """
        Check GPU availability and capabilities

        :return: Dictionary of GPU diagnostics
        """
        try:
            import torch

            return {
                "cuda_available": torch.cuda.is_available(),
                "cuda_device_count": torch.cuda.device_count(),
                "cuda_device_names": (
                    [
                        torch.cuda.get_device_name(i)
                        for i in range(torch.cuda.device_count())
                    ]
                    if torch.cuda.is_available()
                    else []
                ),
            }
        except ImportError:
            return {
                "cuda_available": False,
                "cuda_device_count": 0,
                "cuda_device_names": [],
            }

    def run_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """
        Run comprehensive system diagnostics

        :return: Comprehensive diagnostic report
        """
        return {
            "system_info": self.get_system_info(),
            "dependencies": self.check_ai_dependencies(),
            "gpu_diagnostics": self.gpu_diagnostics(),
            "timestamp": os.getenv("DEPLOYMENT_TIMESTAMP", "Unknown"),
        }

    def export_diagnostics(self, output_path: str = "system_diagnostics.json"):
        """
        Export diagnostic report to a JSON file

        :param output_path: Path to export diagnostic report
        """
        try:
            diagnostics = self.run_comprehensive_diagnostics()

            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(diagnostics, f, indent=4)

            self._logger.info(f"Diagnostic report exported to {output_path}")
        except Exception as e:
            self._logger.error(f"Error exporting diagnostics: {e}")


def main():
    """
    CLI for system diagnostics
    """
    import argparse

    parser = argparse.ArgumentParser(description="AI Teddy Bear System Diagnostics")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="system_diagnostics.json",
        help="Path to export diagnostic report",
    )
    parser.add_argument(
        "-p", "--print", action="store_true", help="Print diagnostic report to console"
    )

    args = parser.parse_args()

    diagnostics = SystemDiagnostics()
    report = diagnostics.run_comprehensive_diagnostics()

    if args.print:
        print(json.dumps(report, indent=4))

    diagnostics.export_diagnostics(args.output)


if __name__ == "__main__":
    main()
