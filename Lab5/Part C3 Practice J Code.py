import requests

base_url = "http://localhost:3000"
search_url = base_url + "/rest/products/search"

probe = requests.get(search_url, params={"q": "'"}, timeout=5)

error_phrases = ["sqlite_error", "syntax error", "sql", "unclosed quotation mark"]

found_errors = []
for phrase in error_phrases:
    if phrase in probe.text.lower():
        found_errors.append(phrase)

print("Status code:", probe.status_code)
if found_errors:
    print("Found database error phrases:", found_errors)
    print("Sample response text:\n", probe.text[:300])
else:
    print("No specified database error phrases found.")