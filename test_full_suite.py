import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

base = "http://127.0.0.1:5000"

def test_endpoint(url, method="GET", data=None, headers=None):
    if headers is None: headers = {}
    if data: 
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), method=method)
        req.add_header("Content-Type", "application/json")
    else:
        req = urllib.request.Request(url, method=method)
    for k, v in headers.items(): req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode("utf-8")

print("=== STARTING SWACHHPULSE END-TO-END TEST ===")

# 1. Test index.html
s, html = test_endpoint(base + "/")
print(f"1. GET / -> Status {s}, size: {len(html)} bytes")
assert "Swachh" in html and "Pulse" in html
assert "Tiranga" in html or "tiranga-accent-bar" in html
assert "github-heatmap-card" in html
assert "tab-academy" in html

# 2. Test Login
s, auth_res = test_endpoint(base + "/api/auth/login", "POST", {"email": "citizen@cleanwaste.org", "password": "citizen123"})
auth_data = json.loads(auth_res)
token = auth_data["token"]
print(f"2. POST /api/auth/login -> Status {s}, User: {auth_data['user']['name']}, Ward: {auth_data['user'].get('address', 'Ward 14')}")

# 3. Test GitHub-style 112-day Heatmap
s, hm_res = test_endpoint(base + "/api/user/heatmap", "GET", headers={"Authorization": f"Bearer {token}"})
hm_data = json.loads(hm_res)
print(f"3. GET /api/user/heatmap -> Status {s}, Total: {hm_data['total_contributions']}, Streak: {hm_data['streak_days']} days, Karma: {hm_data['karma_points']} pts, Squares: {len(hm_data['squares'])}")

# 4. Test AI Swachhata Lessons
s, l_res = test_endpoint(base + "/api/ai/lessons")
l_data = json.loads(l_res)
print(f"4. GET /api/ai/lessons -> Status {s}, Loaded {len(l_data['lessons'])} cultural modules:")
for l in l_data["lessons"]:
    print(f"   Module {l['number']}: {l['title']} ({l['hindiTitle']})")

# 5. Test Swachhata Quiz & Certificate Generation
quiz_payload = {"answers": {"1": 1, "2": 1, "3": 1, "4": 2}, "userName": "Aarav Sharma"}
s, q_res = test_endpoint(base + "/api/ai/quiz", "POST", quiz_payload, headers={"Authorization": f"Bearer {token}"})
q_data = json.loads(q_res)
cert = q_data["certificate"]
print(f"5. POST /api/ai/quiz -> Status {s}, Score: {q_data['percentage']}%, Cert ID: {cert['certificateId']}, Authority: {cert['issuingAuthority']}")

# 6. Test AI Swachhata Guru Chat (Bilingual Indian Cultural Tutor)
chat_prompts = [
    "What should I do with temple puja flowers and garlands (Nirmalya)?",
    "Where should I throw milk packets (Amul/Mother Dairy)?",
    "What is the Sanitary Red Dot rule for Safai Mitras?"
]
print("6. AI Swachhata Guru Interactive Responses:")
for p in chat_prompts:
    s, c_res = test_endpoint(base + "/api/ai/chat", "POST", {"message": p}, headers={"Authorization": f"Bearer {token}"})
    c_data = json.loads(c_res)
    print(f"   Q: {p}")
    print(f"   AI: {c_data['reply'][:130]}...\n")

# 7. Test Admin Analytics & AI Fleet Route Optimizer
s, admin_auth = test_endpoint(base + "/api/auth/login", "POST", {"email": "admin@cleanwaste.org", "password": "admin123"})
admin_token = json.loads(admin_auth)["token"]
s, dash_res = test_endpoint(base + "/api/admin/analytics", "GET", headers={"Authorization": f"Bearer {admin_token}"})
dash_data = json.loads(dash_res)
print(f"7. GET /api/admin/analytics -> Status {s}, Total Complaints: {dash_data['overview']['total_complaints']}, Hotspots: {len(dash_data['hotspots'])}")

s, route_res = test_endpoint(base + "/api/ai/route-optimizer", "GET", headers={"Authorization": f"Bearer {admin_token}"})
route_data = json.loads(route_res)
print(f"8. GET /api/ai/route-optimizer -> Status {s}, Vehicle: {route_data['vehicle_id']}, Stops: {route_data['total_stops']}, Fuel Saved: {route_data['estimated_fuel_saved_liters']} L, CO2 Avoided: {route_data['co2_emissions_avoided_kg']} kg")

# 9. Test Community Upvoting
s, up_res = test_endpoint(base + "/api/complaints/1/upvote", "POST", {}, headers={"Authorization": f"Bearer {token}"})
up_data = json.loads(up_res)
print(f"9. POST /api/complaints/1/upvote -> Status {s}, New Upvotes: {up_data['upvotes']}, Msg: {up_data['message']}")

# 10. Test Harit Tyohar (Green Festivals Guide)
s, fest_res = test_endpoint(base + "/api/festivals", "GET")
fest_data = json.loads(fest_res)
print(f"10. GET /api/festivals -> Status {s}, Loaded {len(fest_data['festivals'])} Green Festivals:")
for f in fest_data['festivals'][:3]:
    print(f"    - {f['icon']} {f['name']}: {f['tagline']}")

# 11. Test Ward Cleanliness Leaderboard
s, lead_res = test_endpoint(base + "/api/wards/leaderboard", "GET")
lead_data = json.loads(lead_res)
print(f"11. GET /api/wards/leaderboard -> Status {s}, Top Ward: {lead_data['leaderboard'][0]['ward']} ({lead_data['leaderboard'][0]['score']}/100 - {lead_data['leaderboard'][0]['status']})")

print("\n🎉 ALL 11 TEST SUITES COMPLETED WITH 100% SUCCESS!")
