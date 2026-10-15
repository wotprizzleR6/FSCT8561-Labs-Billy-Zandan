import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

search_url = base_url + "/rest/products/search"
r = requests.get(search_url, params={"q": "apple"}, timeout=5)

post_response = requests.post(
    search_url,
    data={"q": "apple"},
    timeout=5
)
print("POST status:", post_response.status_code)
print("POST response length:", len(post_response.content))