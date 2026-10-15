import requests

base_url = "http://localhost:3000"

try:
    test_response = requests.get(base_url, timeout=5)
    print("Connected. Status:", test_response.status_code)
except requests.RequestException as error:
    print("Could not connect:", error)