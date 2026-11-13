from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

# Key must always be exactly 8 bytes for DES
key = "mycipher".encode("utf8")

# Any message of any length!
message = "Hello".encode("utf8")

# 1. Encrypt (pad to 8-byte blocks)
cipher = DES.new(key, DES.MODE_ECB)
cipher_text = cipher.encrypt(pad(message, DES.block_size))
print("Encrypted:", cipher_text)

# 2. Decrypt (unpad back to original)
cipher = DES.new(key, DES.MODE_ECB)
decrypted_padded = cipher.decrypt(cipher_text)
plain_text = unpad(decrypted_padded, DES.block_size)
print("Decrypted:", plain_text.decode("utf8"))