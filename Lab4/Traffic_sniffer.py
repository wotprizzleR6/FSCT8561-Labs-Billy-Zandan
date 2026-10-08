import os
from scapy.all import rdpcap, IP, TCP, UDP

# For some reason the .pcap file wont load if I use a relative path, so I used an absolute path instead
PCAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "botnet-capture-20110812-rbot.pcap")

def main():
    print(f"Loading capture file: {PCAP}")
    packets = rdpcap(PCAP)
    print(f"Total packets loaded: {len(packets)}\n")

    tcp_count = 0
    udp_count = 0
    shown = 0

    for pkt in packets:
        # Count all TCP and UDP packets in the full capture
        if IP in pkt:
            if TCP in pkt:
                tcp_count += 1
            elif UDP in pkt:
                udp_count += 1

        # Print the first 20 IPv4 TCP/UDP packets
        if shown < 20 and IP in pkt and (TCP in pkt or UDP in pkt):
            proto = "TCP" if TCP in pkt else "UDP"
            layer = TCP if TCP in pkt else UDP
            src_port = pkt[layer].sport
            dst_port = pkt[layer].dport
            print(
                f"Source: {pkt[IP].src:<16} "
                f"Destination: {pkt[IP].dst:<16} "
                f"Protocol: {proto}  "
                f"Source port: {src_port:<6} "
                f"Destination port: {dst_port}"
            )
            shown += 1

    print()
    print(f"Total TCP packets: {tcp_count}")
    print(f"Total UDP packets: {udp_count}")


if __name__ == "__main__":
    main()

