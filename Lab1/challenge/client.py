import socket
import threading

HOST = "127.0.0.1"
PORT = 12346


def receive_loop(sock: socket.socket) -> None:
    """
    Background thread: continuously read messages pushed by the server
    (i.e. broadcasts from other clients) and print them.
    """
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[Server closed the connection]")
                break
            message = data.decode("utf-8", errors="replace")
            print(f"\n{message}\nYou: ", end="", flush=True)
        except OSError:
            break


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to multi-client server at {HOST}:{PORT}")

        # Step 1: Identify ourselves with HELLO
        username = input("Enter your username: ").strip()
        if not username:
            print("Username cannot be empty. Exiting.")
            return

        client_socket.send(f"HELLO|{username}".encode())
        response = client_socket.recv(1024).decode("utf-8", errors="replace")
        print(f"Server: {response}")

        if response.startswith("ERROR"):
            print("Could not register username. Exiting.")
            return

        # Start the receive thread
        recv_thread = threading.Thread(
            target=receive_loop,
            args=(client_socket,),
            daemon=True
        )
        recv_thread.start()

        # Step 2: Message loop
        print("\nType a message and press Enter to send. Type EXIT to disconnect.\n")

        while True:
            try:
                message = input("You: ").strip()
            except EOFError:
                break

            if message.upper() == "EXIT":
                client_socket.send("EXIT|".encode())

                try:
                    farewell = client_socket.recv(1024).decode("utf-8", errors="replace")
                    print(f"Server: {farewell}")
                except OSError:
                    pass
                break

            # Receive and display the server's acknowledgement
            client_socket.send(f"MSG|{message}".encode())
            # Acknowledgement part
            try:
                ack = client_socket.recv(1024).decode("utf-8", errors="replace")
                print(f"Server: {ack}")
            except OSError:
                break

    except ConnectionRefusedError:
        print(f"ERROR: Could not connect — is challenge/server.py running on port {PORT}?")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        try:
            client_socket.send("EXIT|".encode())
        except OSError:
            pass
    finally:
        client_socket.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()

