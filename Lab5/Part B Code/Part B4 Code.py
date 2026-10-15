import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)
search_url = base_url + "/rest/products/search"
r = requests.get(search_url, params={"q": "apple"}, timeout=5)

def get_status(search_word):
    result = requests.get(search_url, params={"q": search_word}, timeout=5)
    return result.status_code

print(get_status("banana"))