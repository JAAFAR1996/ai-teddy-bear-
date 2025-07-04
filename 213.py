import requests
import os

CODACY_API_TOKEN = "b8a1a1d381dc4001bb4c84bb7d7399b2"
ORGANIZATION = "gh/JAAFAR1996"
REPOSITORY = "ai-teddy-bear-"   # بالضبط كما هو في الرابط
OUTPUT_DIR = "codacy_issues_markdown"

os.makedirs(OUTPUT_DIR, exist_ok=True)

url = f"https://app.codacy.com/api/v3/analysis/organizations/{ORGANIZATION}/repositories/{REPOSITORY}/issues/search"
headers = {
    "api-token": CODACY_API_TOKEN,
    "Content-Type": "application/json"
}

all_issues = []
for page in range(1, 11):  # جرب حتى 10 صفحات (كل صفحة حتى 1000 مشكلة)
    payload = {
        "limit": 1000,
        "page": page,
        "status": "All"
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        print(f"❌ صفحة {page}: فشل الاتصال أو حدث خطأ في الاستعلام!")
        print("الرد:", r.text)
        break
    issues = r.json().get("issues", [])
    print(f"صفحة {page}: عدد المشاكل المستخرجة: {len(issues)}")
    if not issues:
        break
    all_issues.extend(issues)

print(f"\nعدد كل المشاكل المستخرجة: {len(all_issues)}")

for idx, issue in enumerate(all_issues, 1):
    md = f"""# [{issue.get('category', 'Issue')}] {issue.get('tool', '')} – {issue.get('ruleDescription', '')}

**File:** `{issue.get('filename', 'unknown')}`
**Line:** {issue.get('line', 'unknown')}`

---
**Problem:**
> {issue.get('message', '')}

---
**Severity:** {issue.get('severity', 'unknown')}
**Pattern:** {issue.get('patternId', '')}
**Tool:** {issue.get('tool', '')}
"""
    with open(f"{OUTPUT_DIR}/issue_{idx:05}.md", "w", encoding="utf-8") as out:
        out.write(md)

print(f"✅ تم توليد ملفات Markdown لكل مشكلة في مجلد: {OUTPUT_DIR}")
