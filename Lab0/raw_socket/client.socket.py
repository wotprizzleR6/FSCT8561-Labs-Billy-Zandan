# Import the socket module
import socket

# Define server address and port to connect to
HOST = "127.0.0.1"
PORT = 12345

# Create a TCP socket (IPv4, TCP stream)
client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Connect to the server
client_socket.connect((HOST, PORT))

# Prepare message to send
message = "Hello Server, this is Billy Z"

# Send encoded message to the server
client_socket.send(message.encode())

# Receive reply from the server that is up to 1024 bytes
response = client_socket.recv(1024)

# Decode bytes and print the server's reply
print("Server replied:", response.decode())

# Close the client socket connection
client_socket.close()
