"""
Lab 1 — Socket.IO Server Demo
FSCT 8561 — Security Applications

Demonstrates the same stateful chat concept as server.py
but using python-socketio instead of raw TCP sockets.

Install dependencies first:
    pip install python-socketio eventlet

Author: Billy Zandan
"""

import socketio
import eventlet
import eventlet.wsgi

# Create a Socket.IO server (ASGI-compatible)
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Session state: maps socket ID → username
sessions: dict[str, str | None] = {}


@sio.event
def connect(sid, environ):
    """Called automatically when a new client connects."""
    sessions[sid] = None   # no username yet
    print(f"[CONNECT] Client connected: {sid}")


@sio.event
def disconnect(sid):
    """Called automatically when a client disconnects."""
    username = sessions.pop(sid, None)
    print(f"[DISCONNECT] {username or sid} disconnected")


@sio.event
def hello(sid, data):
    """
    Client registers a username.
    Equivalent to sending HELLO|username in the raw TCP protocol.
    """
    username = data.get("username", "").strip()

    if not username:
        sio.emit("error", {"reason": "Username required"}, to=sid)
        return

    sessions[sid] = username
    print(f"[SESSION] Username registered: {username}")
    sio.emit("ok", {"info": f"Hello {username}"}, to=sid)


@sio.event
def message(sid, data):
    """
    Client sends a chat message.
    Equivalent to sending MSG|text in the raw TCP protocol.
    """
    username = sessions.get(sid)

    if username is None:
        sio.emit("error", {"reason": "Send HELLO first"}, to=sid)
        return

    text = data.get("text", "")

    if not text:
        sio.emit("error", {"reason": "Message cannot be empty"}, to=sid)
        return

    if len(text) > 200:
        sio.emit("error", {"reason": "Message too long"}, to=sid)
        return

    print(f"[MSG] {username}: {text}")
    sio.emit("ok", {"info": f"Message received from {username}"}, to=sid)


@sio.event
def exit(sid, data):
    """
    Client signals a clean disconnect.
    Equivalent to sending EXIT| in the raw TCP protocol.
    """
    username = sessions.get(sid)
    print(f"[EXIT] {username or sid} is leaving")
    sio.emit("ok", {"info": "Goodbye"}, to=sid)
    sio.disconnect(sid)


if __name__ == "__main__":
    print("Socket.IO server running on http://127.0.0.1:8765")
    eventlet.wsgi.server(eventlet.listen(("127.0.0.1", 8765)), app)

