import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

search_terms = ["apple", "banana", "orange", "lemon"]

for term in search_terms:
    print("Search term:", term)