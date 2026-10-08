import os
from scapy.all import rdpcap, Raw

# For some reason the .pcap file wont load if I use a relative path, so I used an absolute path instead
PCAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "botnet-capture-20110812-rbot.pcap")

packets = rdpcap(PCAP)

# Step 2. Check whether one packet contains Raw data
pkt = packets[0]
print("Contains Raw payload?", Raw in pkt)

# Step 3. Look at a short payload sample
if Raw in pkt:
    print(repr(bytes(pkt[Raw].load)[:80]))
else:
    print("No Raw payload in this packet")

# Step 4. Find a packet that contains a payload
for pkt in packets:
    if Raw in pkt:
        print("Payload sample:", repr(bytes(pkt[Raw].load)[:80]))
        break

# Step 5. Display a small readable sample
for pkt in packets:
    if Raw in pkt:
        sample = bytes(pkt[Raw].load)[:80]
        print(sample.decode("utf-8", errors="replace"))
        break

# Step 6. Look for familiar HTTP header text
found = False
for pkt in packets[:500]:
    if Raw in pkt:
        data = bytes(pkt[Raw].load)
        if b"User-Agent:" in data:
            print("Possible plaintext HTTP header found")
            found = True
            break
if not found:
    print("No matching header found in the first 500 packets")
