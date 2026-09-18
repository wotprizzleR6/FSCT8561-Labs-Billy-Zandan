import socket
import threading
import datetime


HOST = "127.0.0.1"
PORT = 12346
MAX_MSG_LEN = 200

clients_lock = threading.Lock()
clients: dict[socket.socket, str | None] = {}


def log(label: str, text: str) -> None:
    """Thread-safe timestamped console log."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{label}] {text}")


def broadcast(sender_socket: socket.socket, message: str) -> None:
    """
    Send a message to every connected client except the sender.

    If recipient socket fails, then that client is removed from the pool.
    """
    dead_sockets = []

    with clients_lock:
        for sock in list(clients.keys()):
            if sock is sender_socket:
                continue   
            try:
                sock.send(message.encode())
            except OSError:
                dead_sockets.append(sock)

    # clean up any dead sockets
    for sock in dead_sockets:
        remove_client(sock)


def remove_client(sock: socket.socket) -> None:
    """Safely remove the client and close its socket."""
    with clients_lock:
        username = clients.pop(sock, None)

    try:
        sock.close()
    except OSError:
        pass

    if username:
        log("LEFT", f"{username} has left the server")
        broadcast(sock, f"SERVER|{username} has left the chat")


def handle_client(client_socket: socket.socket, client_address: tuple) -> None:
    """
    Handle one client's entire session in its own thread.
    Mirrors the single-client server logic but also broadcasts messages.
    """
    log("CONNECT", f"New connection from {client_address}")

    # Register with no username for now
    with clients_lock:
        clients[client_socket] = None

    connected = True

    while connected:
        try:
            data = client_socket.recv(1024)

            if not data:
                log("DISCONNECT", f"{client_address} disconnected unexpectedly")
                break

            message = data.decode("utf-8", errors="replace").strip()
            log("RECV", f"{client_address} → {message}")

            if "|" not in message:
                client_socket.send("ERROR|Invalid format — expected COMMAND|DATA".encode())
                continue

            command, content = message.split("|", 1)
            command = command.upper()

            with clients_lock:
                username = clients.get(client_socket)

            # start hello
            if command == "HELLO":
                if content.strip() == "":
                    client_socket.send("ERROR|Username required".encode())
                else:
                    new_name = content.strip()

                    # start the check for duplicate usernames
                    with clients_lock:
                        existing_names = list(clients.values())

                    if new_name in existing_names:
                        client_socket.send(
                            f"ERROR|Username '{new_name}' is already taken".encode()
                        )
                        log("ERROR", f"Duplicate username attempt: {new_name}")
                    else:
                        with clients_lock:
                            clients[client_socket] = new_name

                        client_socket.send(f"OK|Hello {new_name}".encode())
                        log("SESSION", f"User registered: {new_name}")

                        # broadcast new users to other joined users
                        broadcast(client_socket, f"SERVER|{new_name} has joined the chat")

            elif command == "MSG":
                if username is None:
                    client_socket.send("ERROR|Send HELLO first".encode())
                elif content == "":
                    client_socket.send("ERROR|Message cannot be empty".encode())
                elif len(content) > MAX_MSG_LEN:
                    client_socket.send(
                        f"ERROR|Message too long — max {MAX_MSG_LEN} characters".encode()
                    )
                else:
                    # Send acknowledge to sender
                    client_socket.send(f"OK|Message sent".encode())
                    log("MSG", f"{username}: {content}")

                    # Send the broadcast to everyone else
                    broadcast(client_socket, f"MSG|{username}: {content}")

            elif command == "EXIT":
                client_socket.send("OK|Goodbye".encode())
                log("EXIT", f"{username or client_address} exited cleanly")
                connected = False

            else:
                client_socket.send(f"ERROR|Unknown command: {command}".encode())

        except ConnectionResetError:
            log("DISCONNECT", f"Connection reset by {client_address}")
            break
        except OSError as exc:
            log("ERROR", f"Socket error for {client_address}: {exc}")
            break
        except Exception as exc:
            log("ERROR", f"Unexpected: {exc}")
            break

    remove_client(client_socket)


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    log("START", f"Multi-client server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            thread.start()
            log("THREAD", f"Started thread for {client_address} (active: {threading.active_count() - 1})")

    except KeyboardInterrupt:
        log("STOP", "Server interrupted by user")
    finally:
        server_socket.close()
        log("STOP", "Server socket closed")


if __name__ == "__main__":
    main()
