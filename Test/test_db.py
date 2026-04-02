import urllib.request
import json

BASE = "http://localhost:8000"

def get(url):
    try:
        res = urllib.request.urlopen(url)
        return json.loads(res.read())
    except Exception as e:
        return {"error": str(e)}

# First login to get token
import urllib.error

def post(url, data):
    body = json.dumps(data).encode()
    req  = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

print("Checking server is running...")
res = get(f"{BASE}/")
print(f"  {res}")

print("\nLogging in as faculty...")
res = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd",
    "password": "test1234"
})
if "access_token" in res:
    print(f"  Login successful! Role: {res['role']}")
    print(f"  Token: {res['access_token'][:30]}...")
else:
    print(f"  Login failed: {res}")