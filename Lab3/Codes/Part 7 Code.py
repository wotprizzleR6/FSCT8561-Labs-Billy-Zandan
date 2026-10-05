import hashlib
import pyotp

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# Generate a per-user secret so when the user tries to log in, it won't generate a new secret everytime.
alice_secret = pyotp.random_base32()

users = {
    "alice": {
        "password_hash": hash_password(
            "Cyber123!"
        ),
        "totp_secret": alice_secret
    }
}

print(
    "Alice's TOTP secret:",
    users["alice"]["totp_secret"]
)
