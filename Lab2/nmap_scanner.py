import os
import socket
import nmap

# Ensure Nmap directory is included in PATH
nmap_dir = r"C:\Program Files (x86)\Nmap"
if nmap_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = nmap_dir + os.pathsep + os.environ.get("PATH", "")


def main():
    target = input("Target host: ").strip()
    if not target:
        print("Target host cannot be empty.")
        return

    # resolve hostname
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("Invalid hostname or IP address")
        return

    # Ask for start and end port
    try:
        start_port = int(input("Start port: "))
        end_port = int(input("End port: "))
    except ValueError:
        print("Port must be a number")
        return

    # Validate the port range
    if not (1 <= start_port <= 65535):
        print("Invalid start port. Must be between 1 and 65535.")
        return

    if not (1 <= end_port <= 65535):
        print("Invalid end port. Must be between 1 and 65535.")
        return

    if start_port > end_port:
        print("Start port must be less than or equal to end port.")
        return

    if end_port - start_port > 1000:
        print("Range too large. Please scan 1000 ports or fewer at a time.")
        return

    # Perform the scan using python-nmap
    print(f"\nTarget: {target_ip}")
    print(f"Scanning TCP ports {start_port}–{end_port} using Nmap...\n")

    try:
        scanner = nmap.PortScanner()
        port_range_str = f"{start_port}-{end_port}"
        scanner.scan(target_ip, port_range_str)
    except nmap.PortScannerError as e:
        print(f"Nmap scanning error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during scan: {e}")
        return

    # Display discovered ports, states, services
    print(f"{'PORT':<10}{'STATE':<12}{'SERVICE'}")
    print("-" * 32)

    open_ports_count = 0

    if target_ip in scanner.all_hosts() and "tcp" in scanner[target_ip].all_protocols():
        tcp_scan_data = scanner[target_ip]["tcp"]

        for port in sorted(tcp_scan_data.keys()):
            port_info = tcp_scan_data[port]
            state = port_info.get("state", "unknown")
            service = port_info.get("name", "unknown")

            # Only display open or responsive ports
            if state == "open":
                print(f"{port:<10}{state:<12}{service}")
                open_ports_count += 1

    print()
    print("Scan complete.")
    if open_ports_count > 0:
        print(f"{open_ports_count} open port(s) found.")
    else:
        print("No open ports found in the selected range.")


if __name__ == "__main__":
    main()
