import socket

HOST = "127.0.0.1"
PORT = 12345


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        username = input("Enter your username: ").strip()

        if not username:
            print("Username cannot be empty. Exiting.")
            return

        client_socket.send(f"HELLO|{username}".encode())

        response = client_socket.recv(1024).decode("utf-8", errors="replace")
        print(f"Server: {response}")

        if response.startswith("ERROR"):
            print("Server rejected username. Exiting.")
            return

        # start the message loop
        print("\nType a message and press Enter. Type EXIT to disconnect.\n")

        while True:
            try:
                message = input("You: ").strip()
            except EOFError:
                break

            if message.upper() == "EXIT":
                client_socket.send("EXIT|".encode())
                farewell = client_socket.recv(1024).decode("utf-8", errors="replace")
                print(f"Server: {farewell}")
                break

            if not message:
                print("(sending empty message to show server validation)")

            client_socket.send(f"MSG|{message}".encode())

            response = client_socket.recv(1024).decode("utf-8", errors="replace")
            print(f"Server: {response}")

    except ConnectionRefusedError:
        print(f"ERROR: Could not connect to {HOST}:{PORT} — is the server running?")
    except KeyboardInterrupt:
        print("\nInterrupted. Sending EXIT to server...")
        try:
            client_socket.send("EXIT|".encode())
        except OSError:
            pass
    except OSError as exc:
        print(f"Socket error: {exc}")
    finally:
        client_socket.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()

