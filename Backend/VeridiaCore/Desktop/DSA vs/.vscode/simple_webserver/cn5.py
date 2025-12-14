from socket import *

# Define the server port
serverPort = 6789

# Create TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind socket to the port
serverSocket.bind(('', serverPort))

# Start listening for incoming connections
serverSocket.listen(1)
print(f"Listening for connection on port {serverPort}...")

while True:
    # Accept client connection
    connectionSocket, addr = serverSocket.accept()
    print(f"Connection established with: {addr}")

    try:
        # Receive request message
        message = connectionSocket.recv(1024).decode()
        print("Request message:", message)

        # Extract the filename from the GET request
        filename = message.split()[1]  # e.g., /helloworld.html
        f = open(filename[1:])  # remove leading '/' to get file name

        # Read file contents
        outputdata = f.read()

        # Send HTTP response header
        header = "HTTP/1.1 200 OK\r\n\r\n"
        connectionSocket.send(header.encode())

        # Send the actual HTML content
        connectionSocket.send(outputdata.encode())

        print(f"✅ Sent file: {filename[1:]}")
        f.close()

    except FileNotFoundError:
        # Send HTTP 404 response
        header = "HTTP/1.1 404 Not Found\r\n\r\n"
        body = "<html><body><h1>404 Not Found</h1><p>The requested file was not found on this server.</p></body></html>"
        connectionSocket.send(header.encode())
        connectionSocket.send(body.encode())

        print(f"❌ File not found: {filename[1:]}")

    except IndexError:
        # Handle invalid HTTP requests
        print("⚠️ Invalid request received.")
        connectionSocket.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")

    # Close the connection socket
    connectionSocket.close()
    print("Connection closed.\n")
