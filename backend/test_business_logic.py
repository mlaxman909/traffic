import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login
login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "j.sharma@signalai.gov.in", "password": "password123"})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
user_id = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()["id"]

# 12. Decision Queue Auth Test
# Create a temporary recommendation
print("Creating temp AI recommendation...")
rec_res = requests.post(
    f"{BASE_URL}/ai-recommendations",
    json={
        "junction_id": 1,
        "traffic_record_id": 1,
        "recommendation_text": "TEMP_TEST_RECOMMENDATION",
        "reason": "temp_reason_text",
        "current_green_time": 30,
        "suggested_green_time": 40,
        "severity": "LOW"
    },
    headers=headers
)
temp_rec_id = rec_res.json()["id"]

# Approve it
print("Approving temp recommendation...")
app_res = requests.put(
    f"{BASE_URL}/ai-recommendations/{temp_rec_id}",
    json={"status": "APPROVED"},
    headers=headers
)
assert app_res.json()["reviewed_by"] == user_id, f"reviewed_by should be {user_id}, got {app_res.json()['reviewed_by']}"

# 13. Operator Log Test
print("Checking operator logs...")
logs = requests.get(f"{BASE_URL}/operator-logs", headers=headers).json()
found = False
for log in logs:
    if log["entity_type"] == "ai_recommendation" and log["entity_id"] == temp_rec_id and log["action"] == "APPROVE_RECOMMENDATION":
        assert log["user_id"] == user_id, f"operator log user_id should be {user_id}"
        found = True
        # delete temp log
        requests.delete(f"{BASE_URL}/operator-logs/{log['id']}", headers=headers)
assert found, "Operator log not found for AI recommendation approval"

# Delete temp recommendation
requests.delete(f"{BASE_URL}/ai-recommendations/{temp_rec_id}", headers=headers)

# 14. Emergency Routing Auth Test
print("Creating temp emergency route...")
er_res = requests.post(
    f"{BASE_URL}/emergency-routes",
    json={
        "emergency_type": "AMBULANCE",
        "vehicle_id": "TEMP-999",
        "origin_junction_id": 1,
        "destination_junction_id": 2,
        "priority": 1,
        "route_description": "TEMP Route"
    },
    headers=headers
)
temp_er_id = er_res.json()["id"]
assert er_res.json()["created_by"] == user_id, "created_by not set correctly"

# Update/Active
print("Activating temp route...")
act_res = requests.put(
    f"{BASE_URL}/emergency-routes/{temp_er_id}",
    json={"status": "ACTIVE"},
    headers=headers
)
assert act_res.status_code == 200

# Delete temp route
requests.delete(f"{BASE_URL}/emergency-routes/{temp_er_id}", headers=headers)

# Clean up any operator logs from emergency route if necessary
logs = requests.get(f"{BASE_URL}/operator-logs", headers=headers).json()
for log in logs:
    if log["entity_type"] == "emergency_route" and log["entity_id"] == temp_er_id:
        requests.delete(f"{BASE_URL}/operator-logs/{log['id']}", headers=headers)

print("Decision Queue and Emergency Routing Auth Tests Passed!")
