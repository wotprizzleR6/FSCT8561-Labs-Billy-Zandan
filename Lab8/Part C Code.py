from Crypto.Cipher import AES

# AES-128 requires a 16-byte key
key = "secret-key-12345".encode("utf8") 
iv = "This is an IV456".encode("utf8") 

cipher = AES.new(key, AES.MODE_CBC, iv)
# Data must be a multiple of 16 bytes
message = "This is a secret message for lab".encode("utf8")

cipher_text = cipher.encrypt(message)
print(f"AES Encrypted: {cipher_text.hex()}")

# Decrypt using the same IV
decipher = AES.new(key, AES.MODE_CBC, iv)
plain_text = decipher.decrypt(cipher_text)
print(f"Decrypted: {plain_text.decode().strip()}")

# 2. IV Modification Test
iv2 = b"DifferentIV12345"
cipher2 = AES.new(key, AES.MODE_CBC, iv2)
print("Ciphertext with modified IV (hex):", cipher2.encrypt(message).hex())

# 3. Invalid Key Length Error
try:
    bad_key = b"secret" # 6 bytes
    AES.new(bad_key, AES.MODE_CBC, iv)
except ValueError as e:
    print("\nObserved Expected Key Error:", e)

# 4. Message Padding Error & .ljust(16) Fix
try:
    short_msg = b"Short msg" # 9 bytes
    cipher_test = AES.new(key, AES.MODE_CBC, iv)
    cipher_test.encrypt(short_msg)
except ValueError as e:
    print("Observed Expected Padding Error:", e)

# Fixed with .ljust(16)
padded_short = "Short msg".ljust(16).encode()
cipher_fixed = AES.new(key, AES.MODE_CBC, iv)
ct_fixed = cipher_fixed.encrypt(padded_short)
decipher_fixed = AES.new(key, AES.MODE_CBC, iv)
print("Padded message decrypted:", decipher_fixed.decrypt(ct_fixed).decode().strip())
