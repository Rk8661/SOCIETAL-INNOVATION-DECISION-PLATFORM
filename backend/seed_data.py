import requests
import time

API_URL = "http://127.0.0.1:8000/api/v1/submissions"

# Enterprise Demo Data - Rich distribution across domains, priorities, and locations
test_reports = [
    # 🚨 ANOMALY TRIGGER: High Priority - Water (4 reports = 4.0x spike)
    {"text": "The drinking water in our village is contaminated and causing illness.", "district": "Tamar", "pincode": "372900"},
    {"text": "Our village drinking water is contaminated and people are getting sick.", "district": "Tamar", "pincode": "372900"},
    {"text": "Contaminated drinking water in the village is making everyone sick.", "district": "Tamar", "pincode": "372900"},
    {"text": "Severe stomach illness spreading because of contaminated drinking water.", "district": "Tamar", "pincode": "372900"},

    # 🚨 HIGH PRIORITY: Infrastructure/School (2 reports = merges into 1 dossier)
    {"text": "The primary school roof collapsed during the heavy storm.", "district": "Ranchi", "pincode": "834001"},
    {"text": "Our local school ceiling caved in completely during the storm.", "district": "Ranchi", "pincode": "834001"},

    # 🚨 HIGH PRIORITY: Electricity (Single report)
    {"text": "A live high-tension electricity wire fell on the main road, it is extremely dangerous.", "district": "Dhanbad", "pincode": "826001"},

    # ⚠️ MEDIUM PRIORITY: Healthcare (2 reports = merges)
    {"text": "The primary health center has no essential medicines or vaccines in stock.", "district": "Khunti", "pincode": "835210"},
    {"text": "Local clinic ran out of basic drugs and emergency supplies.", "district": "Khunti", "pincode": "835210"},

    # ⚠️ MEDIUM PRIORITY: Roads
    {"text": "The main village road has severe potholes causing daily accidents.", "district": "Giridih", "pincode": "815301"},

    # ⚠️ MEDIUM PRIORITY: Rural Livelihoods
    {"text": "The promised agricultural seed distribution for the monsoon has not arrived.", "district": "Deoghar", "pincode": "814112"},

    # ✅ LOW PRIORITY: Environment
    {"text": "Waste is accumulating near residential houses and smells terrible.", "district": "Bokaro", "pincode": "827001"},

    # ✅ LOW PRIORITY: Civic Administration
    {"text": "Most of the streetlights in Sector 4 are broken and not turning on at night.", "district": "Jamshedpur", "pincode": "831004"}
]

print("Seeding enterprise database with realistic citizen reports...")
for report in test_reports:
    response = requests.post(API_URL, json=report)
    if response.status_code == 200:
        print(f"✅ Submitted: {report['text'][:40]}...")
    else:
        print(f"❌ Failed: {response.text}")

    # 3 second delay prevents SQLite database lock issues
    time.sleep(3)

print("\n🎉 Seeding complete! Wait 10 seconds for AI processing, then refresh your dashboard.")
