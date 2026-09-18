import socket
import datetime

# Configuration
HOST = "127.0.0.1"
PORT = 12345
MAX_MSG_LEN = 200   # the maximum allowed message body length


def log(label: str, text: str) -> None:
    """Print a timestamped log line to the console."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {label}: {text}")


def handle_client(client_socket: socket.socket, client_address: tuple) -> None:
    """
    Manage one complete client session.
    State: username — None until a valid HELLO is received
    """
    log("CONNECT", f"New connection from {client_address}")

    username = None      # session state: not authenticated yet
    connected = True

    while connected:
        try:
            # Receive up to 1024 bytes; strip trailing whitespace/newlines
            data = client_socket.recv(1024)

            # Empty bytes means the client closed the connection
            if not data:
                log("DISCONNECT", f"Client {client_address} disconnected unexpectedly")
                break

            # Decode and strip so terminal newlines don't break matching
            message = data.decode("utf-8", errors="replace").strip()
            log("RECV", message)

            # Format validation — must contain pipe character
            if "|" not in message:
                client_socket.send("ERROR|Invalid format — expected COMMAND|DATA".encode())
                log("ERROR", "Invalid format — no pipe character")
                continue

            command, content = message.split("|", 1)
            command = command.upper()   # normalise to uppercase

            # HELLO — register username
            if command == "HELLO":
                if content.strip() == "":
                    client_socket.send("ERROR|Username required".encode())
                    log("ERROR", "HELLO with empty username")
                else:
                    username = content.strip()
                    response = f"OK|Hello {username}"
                    client_socket.send(response.encode())
                    log("SESSION", f"Username registered: {username}")

            # MSG — send a chat message
            elif command == "MSG":
                if username is None:
                    # Data before HELLO — reject
                    client_socket.send("ERROR|Send HELLO first to start a session".encode())
                    log("ERROR", "MSG received before HELLO")
                elif content == "":
                    client_socket.send("ERROR|Message cannot be empty".encode())
                    log("ERROR", f"{client_address} sent empty message")
                elif len(content) > MAX_MSG_LEN:
                    client_socket.send(
                        f"ERROR|Message too long — max {MAX_MSG_LEN} characters".encode()
                    )
                    log("ERROR", f"Oversized message ({len(content)} chars) from {username}")
                else:
                    log("MSG", f"{username}: {content}")
                    client_socket.send(
                        f"OK|Message received from {username}".encode()
                    )

            # EXIT — clean disconnect
            elif command == "EXIT":
                client_socket.send("OK|Goodbye".encode())
                log("EXIT", f"{username or client_address} disconnected cleanly")
                connected = False

            # Unknown command
            else:
                client_socket.send(f"ERROR|Unknown command: {command}".encode())
                log("ERROR", f"Unknown command '{command}' from {username or client_address}")

        except ConnectionResetError:
            log("DISCONNECT", f"Connection reset by {client_address}")
            break
        except OSError as exc:
            log("ERROR", f"Socket error: {exc}")
            break
        except Exception as exc:
            log("ERROR", f"Unexpected error: {exc}")
            break

    client_socket.close()
    log("CLOSED", f"Socket closed for {client_address}")


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow address reuse immediately after restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    log("START", f"Server listening on {HOST}:{PORT}")

    try:
        # Loop forever — after each client disconnects, wait for the next one
        while True:
            log("WAIT", "Waiting for a new connection...")
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address)
    except KeyboardInterrupt:
        log("STOP", "Server interrupted by user (Ctrl+C)")
    finally:
        server_socket.close()
        log("STOP", "Server socket closed")


if __name__ == "__main__":
    main()
