import socketio
sio = socketio.Client()

@sio.event
def connect():
    print("connection established")
    # Prompt user to type a message, then send it to the server
    message = input("Enter message: ")
    sio.emit('message', message)
    # Disconnect automatically after sending - no Ctrl+C needed
    sio.disconnect()

@sio.event
def disconnect():
    print("disconnected from server")

sio.connect('http://localhost:8080')
sio.wait()
