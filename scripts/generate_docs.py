import argparse
import logging
import os
import shutil
import subprocess


class DocumentationGenerator:
    """
    Automated documentation generation utility
    """

    def __init__(self):
        """
        Initialize documentation generator
        """
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def generate_sphinx_docs(self, output_dir: str = "docs/build"):
        """
        Generate documentation using Sphinx

        :param output_dir: Directory to generate documentation
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Run Sphinx documentation generation
            result = subprocess.run(
                ["sphinx-build", "-b", "html", "docs/source", output_dir],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self._logger.info(
                    f"Sphinx documentation generated successfully in {output_dir}"
                )
                return True
            else:
                self._logger.error(
                    f"Sphinx documentation generation failed: {result.stderr}"
                )
                return False
        except Exception as e:
            self._logger.error(f"Error generating Sphinx documentation: {e}")
            return False

    def generate_markdown_docs(self, output_dir: str = "docs/markdown"):
        """
        Generate markdown documentation from source code

        :param output_dir: Directory to generate markdown documentation
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Use pdoc for markdown generation
            result = subprocess.run(
                ["pdoc", "--html", "--output-dir", output_dir, "src"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self._logger.info(
                    f"Markdown documentation generated successfully in {output_dir}"
                )
                return True
            else:
                self._logger.error(
                    f"Markdown documentation generation failed: {result.stderr}"
                )
                return False
        except Exception as e:
            self._logger.error(f"Error generating markdown documentation: {e}")
            return False

    def generate_api_reference(self, output_dir: str = "docs/api"):
        """
        Generate comprehensive API reference

        :param output_dir: Directory to generate API reference
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Use pydoc-markdown for detailed API reference
            result = subprocess.run(
                [
                    "pydoc-markdown",
                    "-I",
                    "src",
                    "-m",
                    "src.application",
                    "-m",
                    "src.domain",
                    "-m",
                    "src.infrastructure",
                    "--render-toc",
                    "--output",
                    output_dir,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self._logger.info(
                    f"API reference generated successfully in {output_dir}"
                )
                return True
            else:
                self._logger.error(f"API reference generation failed: {result.stderr}")
                return False
        except Exception as e:
            self._logger.error(f"Error generating API reference: {e}")
            return False

    def generate_coverage_report(self, output_dir: str = "docs/coverage"):
        """
        Generate code coverage report

        :param output_dir: Directory to generate coverage report
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Run pytest with coverage
            result = subprocess.run(
                ["pytest", "--cov=src", f"--cov-report=html:{output_dir}", "tests/"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self._logger.info(
                    f"Coverage report generated successfully in {output_dir}"
                )
                return True
            else:
                self._logger.error(
                    f"Coverage report generation failed: {result.stderr}"
                )
                return False
        except Exception as e:
            self._logger.error(f"Error generating coverage report: {e}")
            return False


def main():
    """
    CLI for documentation generation
    """
    parser = argparse.ArgumentParser(
        description="AI Teddy Bear Documentation Generator"
    )
    parser.add_argument(
        "--sphinx", action="store_true", help="Generate Sphinx documentation"
    )
    parser.add_argument(
        "--markdown", action="store_true", help="Generate Markdown documentation"
    )
    parser.add_argument("--api", action="store_true", help="Generate API reference")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--all", action="store_true", help="Generate all documentation")

    args = parser.parse_args()

    doc_generator = DocumentationGenerator()

    if args.all or args.sphinx:
        doc_generator.generate_sphinx_docs()

    if args.all or args.markdown:
        doc_generator.generate_markdown_docs()

    if args.all or args.api:
        doc_generator.generate_api_reference()

    if args.all or args.coverage:
        doc_generator.generate_coverage_report()


if __name__ == "__main__":
    main()
