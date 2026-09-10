import requests

BASE_URL = "http://localhost:8000/api"

# 2. Authenticated Test
print("Testing Login...")
login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "j.sharma@signalai.gov.in", "password": "password123"})
if login_res.status_code == 200:
    token = login_res.json()["access_token"]
    print("Login SUCCESS, token obtained.")
else:
    print(f"Login FAILED: {login_res.status_code} {login_res.text}")
    exit(1)

# 3. Invalid Login
print("Testing Invalid Login...")
bad_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "bad@email.com", "password": "wrong"})
assert bad_res.status_code == 401, f"Expected 401, got {bad_res.status_code}"
print("Invalid Login rejected as expected.")

# 4. /api/auth/me Test
print("Testing /api/auth/me...")
me_res = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
assert me_res.status_code == 200, "Failed /auth/me"
assert me_res.json()["email"] == "j.sharma@signalai.gov.in"
print("/auth/me SUCCESS")

# 5. Missing Token
print("Testing Missing Token...")
missing_res = requests.post(f"{BASE_URL}/ai-recommendations", json={})
assert missing_res.status_code == 401, f"Expected 401, got {missing_res.status_code}"
print("Missing token rejected as expected.")

# 6. Invalid Token
print("Testing Invalid Token...")
inv_res = requests.post(f"{BASE_URL}/ai-recommendations", json={}, headers={"Authorization": "Bearer BAD"})
assert inv_res.status_code == 401, f"Expected 401, got {inv_res.status_code}"
print("Invalid token rejected as expected.")

print("All API tests passed!")
