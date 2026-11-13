import hashlib
password = input("Enter a password: ")
hash_object = hashlib.sha256(password.encode())
print("SHA-256 hash:", hash_object.hexdigest())