import hashlib

# Task F1: Brute Force Admin PIN
target_hash = "81dc9bdb52d04dc20036dbd8313ed055"

print("Starting Brute Force Attack...")
recovered_pin = None

for i in range(10000):
    pin = str(i).zfill(4)
    hashed = hashlib.md5(pin.encode()).hexdigest()
    if hashed == target_hash:
        recovered_pin = pin
        print(f"Iteration {i}: Hash matched.")
        print(f"PIN Found: {pin}")
        break

print(f"Verification: MD5('{recovered_pin}') = {hashlib.md5(recovered_pin.encode()).hexdigest()}")
