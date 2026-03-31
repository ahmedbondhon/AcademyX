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

# Login as faculty
print("Logging in...")
res   = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd", "password": "test1234"
})
token = res.get("access_token")
print(f"  Login OK\n")

# Risk scores for course 1
print("=" * 55)
print("Risk Scores — CSE301 (sorted by risk):")
res = get(f"{BASE}/api/obe/risk/1", token)
if "students" in res:
    print(f"  Total: {res['total']} | "
          f"High: {res['high_risk']} | "
          f"Medium: {res['medium_risk']} | "
          f"Low: {res['low_risk']}\n")
    for s in res["students"]:
        risk_icon = (
            "🔴" if s["risk_level"] == "high"   else
            "🟡" if s["risk_level"] == "medium" else
            "🟢"
        )
        cos = ", ".join(s["at_risk_cos"]) if s["at_risk_cos"] else "none"
        print(f"  {risk_icon} {s['student_name']:15s} | "
              f"Risk: {s['risk_pct']:5.1f}% | "
              f"Early: {s['early_pct']:5.1f}% | "
              f"At-risk COs: {cos}")
else:
    print(f"  Error: {res}")

print("\n" + "=" * 55)
print("All tests complete!")