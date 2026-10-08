import os
from scapy.all import rdpcap, TCP, UDP

# For some reason the .pcap file wont load if I use a relative path, so I used an absolute path instead
PCAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "botnet-capture-20110812-rbot.pcap")

# Read capture file
packets = rdpcap(PCAP)

# Filter TCP packets
tcp_packets = []
for pkt in packets:
    if TCP in pkt:
        tcp_packets.append(pkt)

# Filter TCP port 80 packets
http_packets = []
for pkt in tcp_packets:
    if pkt[TCP].sport == 80 or pkt[TCP].dport == 80:
        http_packets.append(pkt)

# Filter UDP port 53 packets
dns_packets = []
for pkt in packets:
    if UDP in pkt:
        if pkt[UDP].sport == 53 or pkt[UDP].dport == 53:
            dns_packets.append(pkt)

# Output results that answer Checkpoint 1
print("TCP packets:", len(tcp_packets))
print("TCP port 80 packets:", len(http_packets))
print("UDP port 53 packets:", len(dns_packets))
