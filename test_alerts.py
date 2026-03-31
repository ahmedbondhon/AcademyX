import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

def post(url, data, token=None):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:    return json.loads(raw)
        except: return {"error": raw.decode()}

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

# Login
print("Logging in as faculty...")
res   = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd",
    "password": "test1234"
})
token = res.get("access_token")
print(f"  Login OK\n")

# Preview alerts (dry run)
print("=" * 55)
print("Alert Preview — CSE301 (dry run):")
res = get(f"{BASE}/api/alerts/preview/1", token)

if "alerts_log" in res:
    print(f"  Course      : {res['course_name']}")
    print(f"  Dry Run     : {res['dry_run']}")
    print(f"  Total       : {res['total_predicted']} students analysed")
    print(f"  High Risk   : {res['high_risk_count']} students")
    print(f"  Medium Risk : {res['med_risk_count']} students")
    print(f"  Triggered at: {res['triggered_at']}\n")

    print("  Alerts that WOULD be sent:")
    for a in res["alerts_log"]:
        cos = ", ".join(a["at_risk_cos"]) if a["at_risk_cos"] else "none"
        print(f"  → {a['student_name']:15s} | "
              f"{a['risk_level'].upper():6s} | "
              f"Risk: {a['risk_pct']:.1f}% | "
              f"COs: {cos}")
        print(f"    Email: {a['email']}")
        print(f"    Subject: {a['subject']}")
        print()
else:
    print(f"  Error: {res}")

print("=" * 55)
print("Test complete!")
print()
print("NOTE: To send REAL emails, configure SMTP in .env")
print("      and call POST /api/alerts/trigger/1?dry_run=false")