import requests

base_url = "http://localhost:3000"
search_url = base_url + "/rest/products/search"

html_test = "<u>fsct8561-test</u>"
response = requests.get(search_url, params={"q": html_test}, timeout=5)

print("Status:", response.status_code)
if html_test in response.text:
    print("HTML string appears unchanged in the response!")
    print("Snippet:", response.text[:200])
else:
    print("HTML string was filtered, encoded, or not reflected.")