print(" Part 4 - Step 1: Create a Byte Payload ")

# Define fictional target port list
ports = [80, 443, 3478, 5060]

# Convert port integers to comma-separated string
port_text = ",".join(str(port) for port in ports)

# Encode string into UTF-8 bytes for Stepic payload
port_bytes = port_text.encode("utf-8")

print(f"Port list   : {ports}")
print(f"Message     : {port_text}")
print(f"Bytes       : {port_bytes}")
print(f"Total bytes : {len(port_bytes)} bytes")

# Notebook assertion
assert port_text == "80,443,3478,5060", "Port text mismatch!"
print("\nPayload creation assertion passed successfully.")
