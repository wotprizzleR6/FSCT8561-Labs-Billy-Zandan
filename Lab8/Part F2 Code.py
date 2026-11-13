from Crypto.Cipher import DES

key = "security".encode("utf8")
cipher = DES.new(key, DES.MODE_ECB)

# Encrypting two separate data packets
packet_1 = "DATA_REQ".encode("utf8")
packet_2 = "DATA_REQ".encode("utf8")

print(f"Packet 1 Ciphertext: {cipher.encrypt(packet_1).hex()}")
print(f"Packet 2 Ciphertext: {cipher.encrypt(packet_2).hex()}")