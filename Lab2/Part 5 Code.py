target = "127.0.0.1"

start_port = 20
end_port = 30

open_ports = []

for port in range(start_port, end_port + 1):

    if scan_port(target, port): # type: ignore
        print(f"  [OPEN] Port {port} is open")
        open_ports.append(port)

if open_ports:
    print(f"Open ports: {open_ports}")
else:
    print("No open ports found in the selected range.")