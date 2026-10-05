import hashlib

def verify_password(stored_password_hash, entered_password):
    # Hash the provided password using SHA-256
    provided_password_hash = hashlib.sha256(entered_password.encode()).hexdigest()
    
    # Compare the stored password hash with the provided password hash
    return stored_password_hash == provided_password_hash