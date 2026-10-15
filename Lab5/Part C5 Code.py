import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

alerts = []
seen = set()

for message in ["Missing CSP", "Missing CSP", "Missing X-Content-Type-Options"]:
    if message not in seen:
        seen.add(message)
        alerts.append(message)

print("Alerts list:", alerts)