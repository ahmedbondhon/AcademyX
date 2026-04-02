import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000/api/auth"  # change to 8000 if that's your port

def post(url, data):
    body = json.dumps(data).encode()
    req  = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        res  = urllib.request.urlopen(req)
        return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw.decode("utf-8", errors="replace")}
    except Exception as ex:
        return 0, {"error": str(ex)}

print("=" * 50)
print("Test 1 — Register student:")
code, res = post(f"{BASE}/register", {
    "name": "Test Student",
    "email": "student@diu.edu.bd",
    "password": "test1234",
    "role": "student"
})
print(f"  Status: {code}")
print(f"  Response: {json.dumps(res, indent=2)}")

print("=" * 50)
print("Test 2 — Register faculty:")
code, res = post(f"{BASE}/register", {
    "name": "Dr. Rahman",
    "email": "faculty@diu.edu.bd",
    "password": "test1234",
    "role": "faculty"
})
print(f"  Status: {code}")
print(f"  Response: {json.dumps(res, indent=2)}")

print("=" * 50)
print("Test 3 — Login correct password:")
code, res = post(f"{BASE}/login", {
    "email": "student@diu.edu.bd",
    "password": "test1234"
})
print(f"  Status: {code}")
print(f"  Response: {json.dumps(res, indent=2)}")

print("=" * 50)
print("Test 4 — Login wrong password:")
code, res = post(f"{BASE}/login", {
    "email": "student@diu.edu.bd",
    "password": "wrongpassword"
})
print(f"  Status: {code}")
print(f"  Response: {json.dumps(res, indent=2)}")

print("=" * 50)
print("Test 5 — Duplicate email:")
code, res = post(f"{BASE}/register", {
    "name": "Duplicate",
    "email": "student@diu.edu.bd",
    "password": "test1234",
    "role": "student"
})
print(f"  Status: {code}")
print(f"  Response: {json.dumps(res, indent=2)}")