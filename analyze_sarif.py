import json
import sys


def analyze_sarif_file(sarif_path):
    """Analyze SARIF file and extract all issues"""
    try:
        with open(sarif_path, "r", encoding="utf-8") as f:
            sarif_data = json.load(f)

        issues = []
        for run in sarif_data["runs"]:
            for result in run["results"]:
                issue = {
                    "file": result["locations"][0]["physicalLocation"][
                        "artifactLocation"
                    ]["uri"],
                    "line": result["locations"][0]["physicalLocation"]["region"][
                        "startLine"
                    ],
                    "column": result["locations"][0]["physicalLocation"]["region"].get(
                        "startColumn", 1
                    ),
                    "message": result["message"]["text"],
                    "ruleId": result["ruleId"],
                    "level": result.get("level", "warning"),
                }
                issues.append(issue)

        print(f"Total issues found: {len(issues)}")
        print("\nIssues by file:")

        # Group by file
        file_issues = {}
        for issue in issues:
            file_path = issue["file"]
            if file_path not in file_issues:
                file_issues[file_path] = []
            file_issues[file_path].append(issue)

        for file_path, file_issues_list in file_issues.items():
            print(f"\n{file_path}: {len(file_issues_list)} issues")
            for issue in file_issues_list:
                print(f"  - Line {issue['line']}: {issue['message']}")

        return issues

    except Exception as e:
        print(f"Error analyzing SARIF file: {e}")
        return []


if __name__ == "__main__":
    issues = analyze_sarif_file("results.sarif")
