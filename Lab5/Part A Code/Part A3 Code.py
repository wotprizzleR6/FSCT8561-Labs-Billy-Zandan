import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

search_url = base_url + "/rest/products/search"
r = requests.get(search_url, params={"q": "banana"}, timeout=5)

print("Requested URL:", r.url)
print("Status:", r.status_code)
print("Content type:", r.headers.get("Content-Type"))
print("First 150 characters:", r.text[:150])