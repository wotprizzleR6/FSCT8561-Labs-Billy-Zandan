import socket
import hashlib
import pyotp

# User database
def hash_password(password):
    """Return the SHA-256 hex digest of a password string."""
    return hashlib.sha256(password.encode()).hexdigest()

# Generate alice's TOTP secret
alice_secret = pyotp.random_base32()
print(f"[SERVER] Alice's TOTP secret : {alice_secret}")
print(f"[SERVER] Current OTP         : {pyotp.TOTP(alice_secret).now()}")
print(f"[SERVER] (OTP changes every 30 seconds)")
print()

users = {
    "alice": {
        "password_hash": hash_password("Cyber123!"),
        "totp_secret": alice_secret
    }
}

# Helper functions
def verify_password(password, stored_hash):
    """Return True if hash of password matches stored_hash."""
    return hash_password(password) == stored_hash

def verify_otp(secret, otp):
    """Return True if otp is a valid current TOTP for secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)

# Server logic
MAX_FAILED = 3

def handle_client(conn, addr):
    print(f"[SERVER] Connected: {addr}")

    password_verified = False
    authenticated_user = None
    failed_attempts = 0

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print("[SERVER] Client disconnected.")
                break

            message = data.decode().strip()
            print(f"[SERVER] Received: {message}")

            # Lockout check
            if failed_attempts >= MAX_FAILED:
                conn.sendall(
                    "ERROR|too many failed attempts, connection blocked".encode()
                )
                print("[SERVER] Max failed attempts reached. Closing connection.")
                break

            # AUTH message
            if message.startswith("AUTH|"):
                parts = message.split("|")
                if len(parts) != 3:
                    conn.sendall(
                        "ERROR|invalid AUTH format, expected AUTH|user|pass".encode()
                    )
                    continue

                _, username, password = parts

                if username not in users:
                    failed_attempts += 1
                    conn.sendall("ACCESS_DENIED".encode())
                    print(f"[SERVER] Unknown username: {username}")
                    continue

                if verify_password(password, users[username]["password_hash"]):
                    password_verified = True
                    authenticated_user = username
                    conn.sendall("OTP_REQUIRED".encode())
                    live_otp = pyotp.TOTP(users[username]["totp_secret"]).now()
                    print(f"[SERVER] Password verified for {username}. Awaiting OTP.")
                    print(f"[SERVER] >>> Current OTP for {username}: {live_otp} <<<")
                    print(f"[SERVER]     (valid for up to 30 seconds)")
                else:
                    failed_attempts += 1
                    password_verified = False
                    authenticated_user = None
                    conn.sendall("ACCESS_DENIED".encode())
                    print(
                        f"[SERVER] Incorrect password for {username}. "
                        f"Attempts: {failed_attempts}"
                    )

            # OTP message
            elif message.startswith("OTP|"):
                if not password_verified:
                    conn.sendall("ERROR|password not verified yet".encode())
                    continue

                parts = message.split("|")
                if len(parts) != 2:
                    conn.sendall(
                        "ERROR|invalid OTP format, expected OTP|code".encode()
                    )
                    continue

                _, otp_code = parts

                if verify_otp(users[authenticated_user]["totp_secret"], otp_code):
                    failed_attempts = 0  # Reset counter on success
                    conn.sendall("ACCESS_GRANTED".encode())
                    print(f"[SERVER] ACCESS GRANTED for {authenticated_user}")
                    break  # Authentication complete, close connection
                else:
                    failed_attempts += 1
                    password_verified = False
                    authenticated_user = None
                    conn.sendall("ACCESS_DENIED".encode())
                    print(f"[SERVER] Invalid OTP. Attempts: {failed_attempts}")

            # Unknown message
            else:
                conn.sendall("ERROR|unknown command".encode())

    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        conn.close()
        print(f"[SERVER] Connection closed: {addr}")

def start_server(host="127.0.0.1", port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(1)
        print(f"[SERVER] Listening on {host}:{port}")

        while True:
            conn, addr = server_sock.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    start_server()