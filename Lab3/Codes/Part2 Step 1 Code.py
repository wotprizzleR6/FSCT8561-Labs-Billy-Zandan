import hashlib

password = "CybeB123!"

password_bytes = password.encode()

password_hash = hashlib.sha256(
    password_bytes
).hexdigest()

print("Password hash:")
print(password_hash)
