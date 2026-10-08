import os
from scapy.all import rdpcap, IP, TCP, UDP

# For some reason the .pcap file wont load if I use a relative path, so I used an absolute path instead
PCAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "botnet-capture-20110812-rbot.pcap")
WINDOW_SECONDS = 5
THRESHOLD = 20


def main():
    print(f"Loading capture file: {PCAP}")
    packets = rdpcap(PCAP)
    print(f"Total packets loaded: {len(packets)}\n")

    # Keep only IPv4 TCP/UDP packets and sort by timestamp
    relevant = [
        pkt for pkt in packets
        if IP in pkt and (TCP in pkt or UDP in pkt)
    ]
    relevant.sort(key=lambda p: float(p.time))

    # Sliding-window tracking
    ip_timestamps: dict[str, list[float]] = {}
    alerted_ips: set[str] = set()

    tcp_count = 0
    udp_count = 0

    for pkt in relevant:
        src_ip = pkt[IP].src
        ts = float(pkt.time)

        if TCP in pkt:
            tcp_count += 1
        else:
            udp_count += 1

        # Initialise timestamp list for new IPs
        if src_ip not in ip_timestamps:
            ip_timestamps[src_ip] = []

        # Remove timestamps older than the window
        window_start = ts - WINDOW_SECONDS
        ip_timestamps[src_ip] = [
            t for t in ip_timestamps[src_ip] if t >= window_start
        ]

        # Add current timestamp
        ip_timestamps[src_ip].append(ts)

        # Check threshold (alert once per IP)
        if len(ip_timestamps[src_ip]) > THRESHOLD and src_ip not in alerted_ips:
            print(
                f"[ALERT] Unusual traffic from {src_ip}: "
                f"{len(ip_timestamps[src_ip])} packets in the last "
                f"{WINDOW_SECONDS} seconds (threshold = {THRESHOLD})"
            )
            alerted_ips.add(src_ip)

    print()
    print(f"Total TCP packets (IPv4): {tcp_count}")
    print(f"Total UDP packets (IPv4): {udp_count}")
    print(f"Suspicious IPs detected:  {len(alerted_ips)}")

    if alerted_ips:
        print("\nSuspicious source IPs:")
        for ip in sorted(alerted_ips):
            print(f"  {ip}")


if __name__ == "__main__":
    main()

