import socket

def scan_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((target, port))
    sock.close()
    return result == 0

def get_service(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"

# Ask for user input
target = input("Target host: ")

try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("Invalid hostname or IP address")
    exit()

try:
    start_port = int(input("Start port: "))
    end_port = int(input("End port: "))
except ValueError:
    print("Port must be a number")
    exit()

# Validate the port range
if not (1 <= start_port <= 65535):
    print("Invalid start port. Must be between 1 and 65535.")
    exit()

if not (1 <= end_port <= 65535):
    print("Invalid end port. Must be between 1 and 65535.")
    exit()

if start_port > end_port:
    print("Start port must be less than or equal to end port.")
    exit()

if end_port - start_port > 1000:
    print("Range too large. Please scan 1000 ports or fewer at a time.")
    exit()

# Scan
print(f"\nTarget: {target_ip}")
print(f"Scanning TCP ports {start_port}–{end_port}...\n")
print(f"{'PORT':<10}{'STATE':<12}{'SERVICE'}")
print("-" * 32)

open_ports = []

for port in range(start_port, end_port + 1):
    if scan_port(target_ip, port):
        service = get_service(port)
        print(f"{port:<10}{'open':<12}{service}")
        open_ports.append(port)

print()
print("Scan complete.")

if open_ports:
    print(f"{len(open_ports)} open port(s) found.")
else:
    print("No open ports found in the selected range.")
