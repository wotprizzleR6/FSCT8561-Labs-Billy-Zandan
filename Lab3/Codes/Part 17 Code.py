MAX_FAILED = 3

def simulate_auth_attempts(attempts):
    """
    Simulates a series of login attempts.
    """
    failed_attempts = 0

    for i, success in enumerate(attempts, start=1):

        # Lockout check
        if failed_attempts >= MAX_FAILED:
            print(f"  Attempt {i}: BLOCKED - too many failed attempts. "
                  f"Authentication locked.")
            continue

        if success:
            failed_attempts = 0   # Reset counter on success
            print(f"  Attempt {i}: ACCESS_GRANTED  "
                  f"(failed_attempts reset to 0)")
        else:
            failed_attempts += 1  # Increment the counter on failure
            print(f"  Attempt {i}: ACCESS_DENIED   "
                  f"(failed_attempts = {failed_attempts})")


print("=" * 55)
print("TEST: Three consecutive failures -> lockout")
print("=" * 55)
simulate_auth_attempts([False, False, False, False, False])

print()
print("=" * 55)
print("TEST: Two failures then success -> counter resets")
print("=" * 55)
simulate_auth_attempts([False, False, True, False])
