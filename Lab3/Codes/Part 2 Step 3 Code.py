import hashlib

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def verify_password(password, stored_hash):
    return hash_password(password) == stored_hash


stored_hash = hash_password("Cyber123!")

# Test with correct password
print(verify_password("Cyber123!", stored_hash))

# Test with incorrect password
print(verify_password("WrongPassword", stored_hash))
