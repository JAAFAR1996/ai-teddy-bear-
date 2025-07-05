#!/usr/bin/env python3
import re
import json
from collections import defaultdict


class SarifRawExtractor:
    def __init__(self, sarif_file):
        self.sarif_file = sarif_file
        self.issues = []
        self.priority_groups = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "trivial": [],
        }

    def extract_issues_raw(self):
        """استخراج المشاكل من ملف معطوب باستخدام regex"""
        print("استخراج المشاكل باستخدام regex...")

        try:
            with open(self.sarif_file, "r", encoding="utf-8") as f:
                content = f.read()

            # البحث عن patterns للمشاكل
            issue_pattern = r'"level":\s*"([^"]+)".*?"uri":\s*"([^"]+)".*?"startLine":\s*(\d+).*?"text":\s*"([^"]+)".*?"ruleId":\s*"([^"]+)"'

            matches = re.findall(issue_pattern, content, re.DOTALL)

            for match in matches:
                level, uri, line, message, rule_id = match

                issue = {
                    "level": level,
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": uri},
                                "region": {"startLine": int(line)},
                            }
                        }
                    ],
                    "message": {"text": message},
                    "ruleId": rule_id,
                }

                self.issues.append(issue)

            print(f"تم استخراج {len(self.issues)} مشكلة")
            return len(self.issues) > 0

        except Exception as e:
            print(f"خطأ في الاستخراج: {e}")
            return False

    def classify_priority(self, issue):
        rule_id = issue.get("ruleId", "").lower()
        message = issue.get("message", {}).get("text", "").lower()
        level = issue.get("level", "warning").lower()

        # Priority rules mapping
        priority_rules = {
            "trivial": ["trailing-whitespace"],
            "critical": ["error"],
            "high": [],
            "medium": ["lizard_ccn-medium", "lizard_nloc-medium"],
            "low": ["style", "format", "naming"],
        }

        # Check simple rule ID and level matches
        for priority, keywords in priority_rules.items():
            if level == priority:
                return "critical"  # level 'error' maps to 'critical'
            if any(keyword in rule_id for keyword in keywords):
                return priority

        # Handle complex message-based rules
        if "cyclomatic complexity" in message:
            numbers = re.findall(r"(\d+)", message)
            if numbers:
                complexity = int(numbers[0])
                if complexity >= 20:
                    return "critical"
                if complexity >= 15:
                    return "high"
                if complexity >= 11:
                    return "medium"
                return "low"

        if "lines of code" in message:
            numbers = re.findall(r"(\d+)", message)
            if numbers:
                lines = int(numbers[0])
                if lines >= 200:
                    return "critical"
                if lines >= 150:
                    return "high"
                if lines >= 100:
                    return "medium"
                return "low"

        return "medium"  # Default priority

    def group_and_create_files(self):
        """تجميع وإنشاء الملفات"""
        print("تجميع المشاكل...")

        for issue in self.issues:
            priority = self.classify_priority(issue)
            self.priority_groups[priority].append(issue)

        # إنشاء الملفات
        for priority, issues_list in self.priority_groups.items():
            if not issues_list:
                continue

            # إنشاء هيكل SARIF صحيح
            sarif_structure = {
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {"name": "ExtractedIssues", "version": "1.0.0"}
                        },
                        "results": issues_list,
                    }
                ],
            }

            filename = f"sarif_{priority}_priority.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(sarif_structure, f, indent=2, ensure_ascii=False)

            print(f"{priority.upper()}: {len(issues_list)} مشكلة → {filename}")

    def process(self):
        if not self.extract_issues_raw():
            print("فشل في استخراج المشاكل")
            return False

        self.group_and_create_files()

        # إحصائيات
        total = len(self.issues)
        print(f"\nالمجموع: {total} مشكلة")
        for priority, issues in self.priority_groups.items():
            if issues:
                count = len(issues)
                percentage = (count / total) * 100
                print(f"{priority.upper()}: {count} ({percentage:.1f}%)")

        print("تم الانتهاء!")
        return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("الاستخدام: python script.py results.sarif")
        sys.exit(1)

    extractor = SarifRawExtractor(sys.argv[1])
    extractor.process()
