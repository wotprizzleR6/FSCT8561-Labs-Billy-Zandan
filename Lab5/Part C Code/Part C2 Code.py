import requests

base_url = "http://localhost:3000"
search_url = base_url + "/rest/products/search"

html_test = "<u>fsct8561-test</u>"
response = requests.get(search_url, params={"q": html_test}, timeout=5)

normal_input = "apple"
probe_input = "'"

normal = requests.get(search_url, params={"q": normal_input}, timeout=5)
probe = requests.get(search_url, params={"q": probe_input}, timeout=5)

print("Normal input status:", normal.status_code)
print("Probe input status:", probe.status_code)