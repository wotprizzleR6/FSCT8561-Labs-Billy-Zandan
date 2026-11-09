import sys

# Ensure terminal UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def set_LSB(value, bit):
    """Return an integer with its least significant bit set to 0 or 1."""
    if bit not in ("0", "1"):
        raise ValueError("bit must be '0' or '1'")
    return (value & 254) if bit == "0" else (value | 1)

def get_LSB(value):
    return str(value & 1)

print("=== Part 1: Binary and LSB Fundamentals ===")
print("--- 1. Worked Example: value = 150 ---")
value = 150
for bit in ("0", "1"):
    changed = set_LSB(value, bit)
    print(value, format(value, "08b"), "->", changed, format(changed, "08b"), "LSB", get_LSB(changed))

assert set_LSB(150, "1") == 151
assert get_LSB(151) == "1"

print("\n--- 2. Your Turn: value = 201 ---")
value = 201
for bit in ("0", "1"):
    changed = set_LSB(value, bit)
    print(value, format(value, "08b"), "->", changed, format(changed, "08b"), "LSB", get_LSB(changed))

assert set_LSB(201, "0") == 200
assert set_LSB(201, "1") == 201
assert get_LSB(200) == "0"
assert get_LSB(201) == "1"
print("All bit-level assertions passed!")

print("\n--- 3. From Letters to Bits ---")
sample = "HI"
raw = sample.encode("utf-8")
print("Characters :", list(sample))
print("Byte values:", list(raw))
print("Bits       :", " ".join(format(b, "08b") for b in raw))
print("Terminator :", format(0, "08b"))
