import uuid
import hashlib

def hash_password(password):
    salt = uuid.uuid4().hex
    hashed = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return hashed + ":" + salt

def check_password(stored_password, user_input):
    hashed, salt = stored_password.split(":")
    return hashed == hashlib.sha256(salt.encode() + user_input.encode()).hexdigest()

password = input("Enter password: ")
stored = hash_password(password)
print("Stored:", stored)
verify = input("Re-enter password: ")
print("Match:", check_password(stored, verify))