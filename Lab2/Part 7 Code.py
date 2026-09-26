import socket


def scan_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((target, port))
    sock.close()
    return result == 0


# Accept user input
target = input("Target host: ")

try:
    target_ip = socket.gethostbyname(target)
    print("Scanning:", target_ip)
except socket.gaierror:
    print("Invalid hostname or IP address")
    exit()

try:
    start_port = int(input("Start port: "))
    end_port = int(input("End port: "))
except ValueError:
    print("Port must be a number")
    exit()

# Scan the port range
open_ports = []

for port in range(start_port, end_port + 1):
    if scan_port(target_ip, port):
        print(f"  [OPEN] Port {port} is open")
        open_ports.append(port)

if open_ports:
    print(f"Open ports: {open_ports}")
else:
    print("No open ports found in the selected range.")
