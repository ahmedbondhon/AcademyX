import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

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

def get(url, token):
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:    return json.loads(raw)
        except: return {"error": raw.decode()}

res   = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd", "password": "test1234"
})
token = res.get("access_token")

print("CO Attainment (tells us marks exist):")
res = get(f"{BASE}/api/obe/co-attainment/1", token)
for r in res.get("results", []):
    print(f"  {r['co']} — {r['total_students']} students, "
          f"{r['passing_students']} passing")