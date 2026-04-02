import urllib.request
import urllib.error
import json
import os

BASE = "http://localhost:8000"

def post(url, data, token=None):
    body    = json.dumps(data).encode()
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

def get(url, token, binary=False):
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        res = urllib.request.urlopen(req)
        return res.read() if binary else json.loads(res.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:    return json.loads(raw)
        except: return {"error": raw.decode()}

# Login
print("Logging in...")
res   = post(f"{BASE}/api/auth/login", {
    "email": "faculty@diu.edu.bd", "password": "test1234"
})
token = res.get("access_token")
print(f"  Login OK\n")

# Test 1 — Download Excel template
print("=" * 55)
print("Test 1 — Download Excel template for course 1:")
data = get(f"{BASE}/api/upload/template/1", token, binary=True)
if isinstance(data, bytes) and len(data) > 0:
    path = "marks_template.xlsx"
    with open(path, "wb") as f:
        f.write(data)
    print(f"  Template downloaded: {path} ({len(data):,} bytes)")
    print(f"  File exists: {os.path.exists(path)}")
else:
    print(f"  Error: {data}")

# Test 2 — Generate PDF report
print("\n" + "=" * 55)
print("Test 2 — Generate OBE PDF report for course 1:")
data = get(f"{BASE}/api/reports/obe/1", token, binary=True)
if isinstance(data, bytes) and data[:4] == b"%PDF":
    path = "OBE_Report_CSE301.pdf"
    with open(path, "wb") as f:
        f.write(data)
    print(f"  PDF generated: {path} ({len(data):,} bytes)")
    print(f"  File exists: {os.path.exists(path)}")
    print(f"  Valid PDF: {data[:4] == b'%PDF'}")
else:
    print(f"  Error: {data}")

# Test 3 — Upload CSV marksheet (preview mode)
print("\n" + "=" * 55)
print("Test 3 — Upload CSV marksheet (preview):")

# Create a small test CSV
csv_content = """student_id,assessment_id,obtained_marks
1,1,8.5
1,2,7.0
2,1,6.0
2,2,9.0
"""
with open("test_marks.csv", "w") as f:
    f.write(csv_content)

# Upload using multipart
import urllib.parse
boundary = "----FormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test_marks.csv"\r\n'
    f"Content-Type: text/csv\r\n\r\n"
    f"{csv_content}\r\n"
    f"--{boundary}--\r\n"
).encode()

req = urllib.request.Request(
    f"{BASE}/api/upload/marksheet?save=false",
    data=body,
    headers={
        "Authorization":  f"Bearer {token}",
        "Content-Type":   f"multipart/form-data; boundary={boundary}",
    }
)
try:
    res  = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print(f"  Status  : {data.get('status')}")
    print(f"  Summary : {data.get('summary')}")
    print(f"  Valid   : {data.get('valid')}")
    print(f"  Errors  : {data.get('errors')}")
except urllib.error.HTTPError as e:
    print(f"  Error: {e.read().decode()}")

print("\n" + "=" * 55)
print("All tests complete!")
print()
print("Check your D:\\Projects\\academiq\\ folder for:")
print("  marks_template.xlsx  — Excel template to fill")
print("  OBE_Report_CSE301.pdf — Open this to see the report!")