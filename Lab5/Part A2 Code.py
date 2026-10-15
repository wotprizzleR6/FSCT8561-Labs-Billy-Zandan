import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

print("HTTP status:", response.status_code)
print("Response length:", len(response.content), "bytes")
print("Content type:", response.headers.get("Content-Type"))
print("First 100 characters:", response.text[:50])