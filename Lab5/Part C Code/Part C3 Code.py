import requests

base_url = "http://localhost:3000"
search_url = base_url + "/rest/products/search"

probe = requests.get(search_url, params={"q": "'"}, timeout=5)

error_phrase = "SQLITE_ERROR"

if error_phrase.lower() in probe.text.lower():
    print("Database-related error text found; manual review required")
else:
    print("No matching database error text in this response")