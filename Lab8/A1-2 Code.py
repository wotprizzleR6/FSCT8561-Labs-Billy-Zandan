import hashlib
password = input("Enter a password: ")
hash_object = hashlib.md5(password.encode())
print("MD5 hash:", hash_object.hexdigest())