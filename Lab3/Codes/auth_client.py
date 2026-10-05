# auth_client.py
# Part 11 - Authentication Client
# FSCT 8561 Lab 3

import socket
from getpass import getpass

def start_client(host="127.0.0.1", port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        try:
            client_sock.connect((host, port))
        except ConnectionRefusedError:
            print("[CLIENT] ERROR: Could not connect. Is auth_server.py running?")
            return

        print(f"[CLIENT] Connected to {host}:{port}")
        print()

        # Collect credentials
        username = input("Username: ")
        password = getpass("Password: ")
        # NOTE: getpass() hides typing on screen only

        # Send AUTH message
        auth_message = f"AUTH|{username}|{password}"
        client_sock.sendall(auth_message.encode())

        # Wait for server response
        response = client_sock.recv(1024).decode().strip()
        print(f"\n[CLIENT] Server response: {response}")

        if response == "OTP_REQUIRED":
            # Password was correct, now collect and send OTP
            print("[CLIENT] Password accepted. Enter your 6-digit OTP code.")
            otp_code = input("OTP code: ")

            otp_message = f"OTP|{otp_code}"
            client_sock.sendall(otp_message.encode())

            final_response = client_sock.recv(1024).decode().strip()
            print(f"[CLIENT] Final result: {final_response}")

            if final_response == "ACCESS_GRANTED":
                print("[CLIENT] *** Authentication successful! Access granted. ***")
            elif final_response == "ACCESS_DENIED":
                print("[CLIENT] OTP was incorrect or expired. Access denied.")
            elif final_response.startswith("ERROR|"):
                error_detail = final_response.split("|", 1)[1]
                print(f"[CLIENT] Server error: {error_detail}")
            else:
                print(f"[CLIENT] Unexpected response: {final_response}")

        elif response == "ACCESS_DENIED":
            # Invalid username OR wrong password, server doesn't say which
            print("[CLIENT] Access denied — invalid username or password.")

        elif response.startswith("ERROR|"):
            error_detail = response.split("|", 1)[1]
            print(f"[CLIENT] Server error: {error_detail}")

        else:
            print(f"[CLIENT] Unexpected server response: {response}")

    print("\n[CLIENT] Connection closed.")

if __name__ == "__main__":
    start_client()