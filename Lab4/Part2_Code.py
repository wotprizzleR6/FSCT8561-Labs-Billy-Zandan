import os
from scapy.all import rdpcap, IP, TCP

# For some reason the .pcap file wont load if I use a relative path, so I used an absolute path instead
PCAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "botnet-capture-20110812-rbot.pcap")

packets = rdpcap(PCAP)

# Pre-build tcp_packets list (used in Step 5)
tcp_packets = []
for pkt in packets:
    if TCP in pkt:
        tcp_packets.append(pkt)

# Step 1. Display all fields of one packet
packets[0].show()

# Step 2. Identify IP packets
pkt = packets[0]
print("Contains IPv4?", IP in pkt)

# Step 3. Read source and destination IP addresses
if IP in pkt:
    print("Source IP:", pkt[IP].src)
    print("Destination IP:", pkt[IP].dst)

# Step 4. Inspect the first five IPv4 packets
shown = 0
for pkt in packets:
    if IP in pkt:
        print(pkt[IP].src, "->", pkt[IP].dst)
        shown = shown + 1
        if shown == 5:
            break

# Step 5. Read TCP flags
if len(tcp_packets) > 0:
    pkt = tcp_packets[0]
    print("TCP flags:", pkt[TCP].flags)

# Step 6. Read packet size and timestamp
pkt = packets[0]
print("Size (bytes):", len(pkt))
print("Timestamp:", float(pkt.time))

# Step 7. Put the fields together for five packets
shown = 0
for pkt in packets:
    if IP in pkt:
        print("Source:", pkt[IP].src, "Destination:", pkt[IP].dst,
              "Bytes:", len(pkt), "Time:", float(pkt.time))
        shown = shown + 1
        if shown == 5:
            break
