from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
import time

password = "mypassword"
# 1. Random Salt Key Derivation
salt1 = Random.new().read(16)
key1 = PBKDF2(password, salt1, dkLen=16, count=10000)
salt2 = Random.new().read(16)
key2 = PBKDF2(password, salt2, dkLen=16, count=10000)
print("Key with Random Salt 1:", key1.hex())
print("Key with Random Salt 2:", key2.hex())

# 2. Fixed Salt Key Derivation (Deterministic)
fixed_salt = b"fixedsalt123456"
key_fixed_1 = PBKDF2(password, fixed_salt, dkLen=16, count=10000)
key_fixed_2 = PBKDF2(password, fixed_salt, dkLen=16, count=10000)
print("\nFixed Salt Key Run 1:", key_fixed_1.hex())
print("Fixed Salt Key Run 2:", key_fixed_2.hex())
print("Fixed Salt Keys Match:", key_fixed_1 == key_fixed_2)

# 3. Iteration Work Factor Benchmark (100 vs 100,000)
t0 = time.perf_counter()
k_100 = PBKDF2(password, fixed_salt, dkLen=16, count=100)
t_100 = time.perf_counter() - t0

t0 = time.perf_counter()
k_100000 = PBKDF2(password, fixed_salt, dkLen=16, count=100000)
t_100000 = time.perf_counter() - t0

print(f"\nIteration Benchmark:")
print(f"  Count = 100:     {t_100*1000:.3f} ms | Key: {k_100.hex()[:16]}...")
print(f"  Count = 100,000: {t_100000*1000:.3f} ms | Key: {k_100000.hex()[:16]}...")
print(f"  Work Factor Increase: {t_100000 / t_100:.1f}x slower")

