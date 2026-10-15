import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)
search_url = base_url + "/rest/products/search"
r = requests.get(search_url, params={"q": "apple"}, timeout=5)

observation = {
    "method": "GET",
    "endpoint": "/rest/products/search",
    "status_code": r.status_code,
    "response_length": len(r.content),
    "content_type": r.headers.get("Content-Type"),
}

print(observation["content_type"])
print("Status:", observation["status_code"])