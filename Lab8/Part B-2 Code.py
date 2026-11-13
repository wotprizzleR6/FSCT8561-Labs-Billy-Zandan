from Crypto.Cipher import DES

# 1. Base 8-byte DES-ECB Encryption & Decryption
key = b"mycipher"
message = b"message "

cipher = DES.new(key, DES.MODE_ECB)
ciphertext = cipher.encrypt(message)
print("Ciphertext (hex):", ciphertext.hex())

decipher = DES.new(key, DES.MODE_ECB)
decrypted = decipher.decrypt(ciphertext)
print("Decrypted:", decrypted.decode())

# 2. Block Alignment Error & .ljust(8) Fix
try:
    bad_msg = "hello".encode()
    cipher.encrypt(bad_msg)
except ValueError as e:
    print("\nObserved Expected Error on 5-byte message:", e)

# Fix with .ljust(8)
padded_msg = "hello".ljust(8).encode()
fixed_ciphertext = cipher.encrypt(padded_msg)
print("Padded message encrypted (hex):", fixed_ciphertext.hex())
print("Padded message decrypted:", decipher.decrypt(fixed_ciphertext).decode().strip())

# 3. Key Change Test
new_key = b"newkey12"
new_cipher = DES.new(new_key, DES.MODE_ECB)
new_ct = new_cipher.encrypt(message)
print("\nNew Key Ciphertext (hex):", new_ct.hex())
print("Decrypting with old key:", decipher.decrypt(new_ct))
