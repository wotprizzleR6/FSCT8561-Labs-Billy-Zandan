from cryptography.fernet import Fernet, InvalidToken

print(" 1. Base Fernet Encryption & Decryption ")
key = Fernet.generate_key()
cipher = Fernet(key)
print(f"Generated Key: {key.decode()}")

message = "Secret message".encode()
encrypted = cipher.encrypt(message)
print("Encrypted Token:", encrypted.decode())

decrypted = cipher.decrypt(encrypted)
print("Decrypted Message:", decrypted.decode())

print("\n 2. Run Multiple Times")
# Encrypt the exact same message with the same key again
encrypted2 = cipher.encrypt(message)
print("Encrypted Run 1:", encrypted.decode())
print("Encrypted Run 2:", encrypted2.decode())
print("Tokens Match?   ", encrypted == encrypted2)

print("\n 3. Save Key to File & Reload ")
# Save key to file
with open("secret.key", "wb") as key_file:
    key_file.write(key)
print("Key saved to 'secret.key'")

# Load key back from file and decrypt
with open("secret.key", "wb") as key_file:
    key_file.write(key)

with open("secret.key", "rb") as key_file:
    saved_key = key_file.read()

loaded_cipher = Fernet(saved_key)
print("Decrypted using loaded key:", loaded_cipher.decrypt(encrypted).decode())

print("\n 4. Modifying Key (Wrong Key Test) ")
wrong_key = Fernet.generate_key()
wrong_cipher = Fernet(wrong_key)
try:
    wrong_cipher.decrypt(encrypted)
except InvalidToken:
    print("Caught InvalidToken error: Decryption failed because the key is incorrect or the ciphertext was tampered with.")
