import requests

base_url = "http://localhost:3000"
response = requests.get(base_url, timeout=5)

server_header = response.headers.get("Server")

print("Server header value:", server_header)