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
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return json.loads(raw)
        except:
            return {"error": raw.decode()}

# Step 1 — Login as faculty
print("Logging in as faculty...")
res = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd",
    "password": "test1234"
})
token = res.get("access_token")
if not token:
    print(f"  Login failed: {res}")
    exit()
print(f"  Login OK — token received\n")

# Step 2 — CO Attainment for course 1
print("=" * 55)
print("CO Attainment — CSE301 Data Structures:")
res = get(f"{BASE}/api/obe/co-attainment/1", token)
if "results" in res:
    for r in res["results"]:
        bar   = "█" * int(r["attainment_pct"] / 5)
        check = "✓" if r["threshold_met"] else "✗"
        print(f"  {check} {r['co']} | {r['attainment_pct']:5.1f}% | "
              f"Level {r['level']} — {r['level_label']:20s} | {bar}")
else:
    print(f"  Error: {res}")

# Step 3 — PO Attainment for program 1
print("\n" + "=" * 55)
print("PO Attainment — BSc CSE Program:")
res = get(f"{BASE}/api/obe/po-attainment/1", token)
if "results" in res:
    for r in res["results"]:
        check = "✓" if r["threshold_met"] else "✗"
        print(f"  {check} {r['po']} | {r['attainment_pct']:5.1f}% | "
              f"{r['level_label']}")
else:
    print(f"  Error: {res}")

# Step 4 — Course Summary
print("\n" + "=" * 55)
print("Course Summary — CSE301:")
res = get(f"{BASE}/api/obe/course-summary/1", token)
if "course_name" in res:
    print(f"  Course    : {res['course_name']}")
    print(f"  Semester  : {res['semester']}")
    print(f"  Students  : {res['student_count']}")
    print(f"  COs Met   : {res['cos_met']} / {res['total_cos']}")
    print(f"  Avg Score : {res['avg_attainment']}%")
    print(f"  Health    : {res['health']}")
else:
    print(f"  Error: {res}")

# Step 5 — Faculty courses
print("\n" + "=" * 55)
print("My Courses (faculty view):")
res = get(f"{BASE}/api/obe/my-courses", token)
if isinstance(res, list):
    for c in res:
        print(f"  {c['course_code']} — {c['course_name']} | "
              f"Health: {c['health']} | Avg: {c['avg_attainment']}%")
else:
    print(f"  Error: {res}")

print("\n" + "=" * 55)
print("All tests complete!")