print("Part 2: Calculate Capacity Before Writing")

def max_message_bytes(width, height, channels=4, terminator_bytes=1):
    capacity_bytes = (width * height * channels) // 8
    return max(0, capacity_bytes - terminator_bytes)

print("100x100 RGBA capacity:", max_message_bytes(100, 100, 4), "message bytes")
print("100x100 RGB capacity :", max_message_bytes(100, 100, 3), "message bytes")

payload = "TARGET:192.168.1.50"
raw_bytes = payload.encode("utf-8")
required_bytes = len(raw_bytes) + 1  # 19 ASCII characters + 1 null terminator = 20 bytes

print(f"\nPayload string       : '{payload}'")
print(f"Payload character count: {len(payload)} characters")
print(f"Payload + terminator : {required_bytes} bytes")
print(f"Pixels needed (RGBA) : {required_bytes * 2} pixels (2 pixels per byte)")

assert required_bytes in (20, 21), f"Unexpected byte count: {required_bytes}"
print("Capacity assertions passed successfully.")
