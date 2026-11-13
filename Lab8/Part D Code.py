from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random

password = "mypassword"
salt = Random.new().read(16)

key = PBKDF2(password, salt, dkLen=16, count=10000)
print("Key:", key)