import requests
import json

BASE_URL = "http://localhost:8000/api"

print("Logging in to get token...")
login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "j.sharma@signalai.gov.in", "password": "password123"})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Running AI recommendation engine...")
gen_res = requests.post(f"{BASE_URL}/ai-recommendations/generate", headers=headers)
print("Status:", gen_res.status_code)
if gen_res.status_code == 200:
    data = gen_res.json()
    print("Analyzed:", data["analyzed_junctions"])
    print("Generated:", data["recommendations_generated"])
    print("Skipped:", data["skipped_duplicate"])
    for d in data["details"]:
        print(" ->", d)
else:
    print(gen_res.text)

print("Checking pending recommendations in Decision Queue...")
q_res = requests.get(f"{BASE_URL}/ai-recommendations?status=PENDING", headers=headers)
print("Pending records found:", len(q_res.json()))
for rec in q_res.json():
    print(f" - {rec['id']}: {rec['severity']} - {rec['recommendation_text']}")
