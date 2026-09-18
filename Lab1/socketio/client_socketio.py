"""
Lab 1 — Socket.IO Client Demo
FSCT 8561 — Security Applications

Connects to the Socket.IO server and demonstrates the same
HELLO / MSG / EXIT flow as the raw TCP client.

Install dependencies first:
    pip install "python-socketio[client]"

Author: Billy Zandan
"""

import socketio

# Create a Socket.IO client
sio = socketio.Client()


@sio.event
def connect():
    print("[CONNECTED] Successfully connected to Socket.IO server")


@sio.event
def disconnect():
    print("[DISCONNECTED] Connection closed")


@sio.event
def ok(data):
    """Server acknowledged a command successfully."""
    print(f"Server OK: {data.get('info', '')}")


@sio.event
def error(data):
    """Server reported an error."""
    print(f"Server ERROR: {data.get('reason', 'Unknown error')}")


def main():
    try:
        sio.connect("http://127.0.0.1:8765")
    except Exception as exc:
        print(f"Could not connect: {exc}")
        print("Is socketio_demo/server_socketio.py running?")
        return

    # ── HELLO ──────────────────────────────────────────────────────────────────
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        sio.disconnect()
        return

    sio.emit("hello", {"username": username})
    sio.sleep(0.5)   # give the server a moment to respond

    # ── Message loop ───────────────────────────────────────────────────────────
    print("\nType a message and press Enter. Type EXIT to disconnect.\n")

    while sio.connected:
        try:
            text = input("You: ").strip()
        except EOFError:
            break

        if text.upper() == "EXIT":
            sio.emit("exit", {})
            sio.sleep(0.3)
            break

        sio.emit("message", {"text": text})
        sio.sleep(0.3)   # brief pause to receive the server's response

    if sio.connected:
        sio.disconnect()

    print("Done.")


if __name__ == "__main__":
    main()

