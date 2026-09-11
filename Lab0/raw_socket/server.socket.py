# Import the socket module
import socket

# Define server address and port
HOST = "127.0.0.1"
PORT = 12345

# Create a TCP socket (IPv4, TCP stream)
server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Bind the socket to the host address and port
server_socket.bind((HOST, PORT))
# Listen for incoming client connections (queue up to 1)
server_socket.listen(1)

print("Server is waiting for a connection...")

# Wait and accept an incoming client connection
client_socket, client_address = server_socket.accept()
print("Connected by:", client_address)

# Receive up to 1024 bytes of data from the client
data = client_socket.recv(1024)

# Decode received bytes into a string
message = data.decode()
print("Client says:", message)

# Prepare reply message
reply = "Received your message Billy, thanks"

# Send encoded reply back to the client
client_socket.send(reply.encode())

# Close client and server sockets
client_socket.close()
server_socket.close()
