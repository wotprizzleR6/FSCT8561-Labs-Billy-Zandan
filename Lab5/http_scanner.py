import csv
import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 5
OUTPUT_FILE = "http_scan_results.csv"

# Define all test cases including endpoint, method, payload/params)
test_cases = [
    {"endpoint": "/",                    "method": "GET",  "payload": None},
    {"endpoint": "/rest/products/search","method": "GET",  "payload": {"q": "apple"}},
    {"endpoint": "/rest/products/search","method": "GET",  "payload": {"q": "banana"}},
    {"endpoint": "/rest/products/search","method": "POST", "payload": {"q": "apple"}},
]


def scan_endpoint(endpoint, method, payload):
    """Send one HTTP request and return an observation dictionary."""
    url = BASE_URL + endpoint
    observation = {
        "endpoint":        endpoint,
        "method":          method,
        "input_payload":   str(payload),
        "status_code":     None,
        "response_length": None,
        "content_type":    None,
        "server":          None,
        "error":           None,
    }

    try:
        if method == "GET":
            r = requests.get(url, params=payload, timeout=TIMEOUT)
        elif method == "POST":
            r = requests.post(url, data=payload, timeout=TIMEOUT)
        else:
            observation["error"] = f"Unsupported method: {method}"
            return observation

        observation["status_code"]     = r.status_code
        observation["response_length"] = len(r.content)
        observation["content_type"]    = r.headers.get("Content-Type", "N/A")
        observation["server"]          = r.headers.get("Server", "N/A")

    except requests.RequestException as err:
        observation["error"] = str(err)

    return observation


def print_observation(obs):
    """Print a single observation in a readable format."""
    print("-" * 60)
    for key, value in obs.items():
        print(f"  {key:<18}: {value}")


def main():
    print(f"HTTP Scanner – Target: {BASE_URL}\n")
    results = []

    for case in test_cases:
        obs = scan_endpoint(case["endpoint"], case["method"], case["payload"])
        print_observation(obs)
        results.append(obs)

    # Save to CSV
    fieldnames = ["endpoint", "method", "input_payload", "status_code",
                  "response_length", "content_type", "server", "error"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[+] Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

