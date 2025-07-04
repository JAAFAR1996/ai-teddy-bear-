import requests

CODACY_API_TOKEN = "1z6WJHo2nom5FU2oAJza"
ORGANIZATION = "gh/JAAFAR1996"

url = f"https://app.codacy.com/api/v3/analysis/organizations/{ORGANIZATION}/repositories"
headers = {
    "api-token": CODACY_API_TOKEN,
    "Content-Type": "application/json"
}

r = requests.get(url, headers=headers)
print(r.status_code)
print(r.text)
