import os
import nmap

# To make sure Nmap is found in PATH (I was having errors with it not being found)
nmap_dir = r"C:\Program Files (x86)\Nmap"
if nmap_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = nmap_dir + os.pathsep + os.environ.get("PATH", "")

# Step 3
scanner = nmap.PortScanner()

# Step 4
target = "127.0.0.1"

scanner.scan(
    target,
    "20-100"
)

# Step 5
print("\nHosts Discovered")
print(scanner.all_hosts())

print("\nProtocols Discovered")
protocols = scanner[target].all_protocols()
print(protocols)

print("\nTCP Port Details")
if "tcp" in protocols:
    print(scanner[target]["tcp"])
else:
    print("No open/responsive TCP ports found in range 20-100.")