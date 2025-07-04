import json
import os

import requests

TOKEN = os.getenv("CODACY_API_TOKEN")  # ضبطه في متغير بيئة بعد تشغيل السكربت
ORG = "gh"
OWNER = "JAAFAR1996"
REPO = "ai-teddy-bear-"

URL = f"https://app.codacy.com/api/v3/analysis/organizations/{ORG}/{OWNER}/repositories/{REPO}/issues/search"
HEADERS = {"api-token": TOKEN, "Content-Type": "application/json"}
OUTPUT_JSON = "all_issues.json"
OUTPUT_MD = "codacy_issues_markdown"


def fetch_all_issues():
    all_issues = []
    payload = {
        "levels": ["Error", "Warning", "Info"],
        "categories": [
            "Security",
            "Code style",
            "Error prone",
            "Best practice",
            "Performance",
            "Code complexity",
        ],
        "status": "All",
        "limit": 1000,
    }
    cursor = None

    while True:
        if cursor:
            payload["cursor"] = cursor
        r = requests.post(URL, headers=HEADERS, json=payload)
        if r.status_code != 200:
            print("❌ خطأ API:", r.status_code, r.text)
            break

        data = r.json()
        issues = data.get("issues", [])
        print(f"Fetched {len(issues)} issues")
        all_issues.extend(issues)

        cursor = data.get("cursor")
        if not cursor or not issues:
            break

    return all_issues


def save_results(issues):
    os.makedirs(OUTPUT_MD, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)
    print(f"✅ JSON saved to {OUTPUT_JSON}")

    for idx, issue in enumerate(issues, 1):
        md = f"""# [{issue.get("category", "Issue")}] {issue.get("tool", "")} – {issue.get("ruleDescription", "")}

**File:** `{issue.get("filename", "unknown")}`
**Line:** {issue.get("line", "unknown")}`

---
**Problem:**
> {issue.get("message", "")}

---
**Severity:** {issue.get("severity", "unknown")}
**Pattern:** {issue.get("patternId", "")}
**Tool:** {issue.get("tool", "")}
"""
        with open(f"{OUTPUT_MD}/issue_{idx:05}.md", "w", encoding="utf-8") as out:
            out.write(md)
    print(f"✅ Markdown: {len(issues)} issues in `{OUTPUT_MD}`")


if __name__ == "__main__":
    issues = fetch_all_issues()
    print(f"\n🚀 Total issues fetched: {len(issues)}\n")
    if issues:
        save_results(issues)
