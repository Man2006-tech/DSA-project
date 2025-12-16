import socket
import os

def main():
    port = 5005
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)

    print(f"Listening for connection on port {port} ....")

    while True:
        client_socket, client_address = server_socket.accept()
        print("New client connected:", client_address)

        # Read the request from the browser
        request = client_socket.recv(1024).decode('utf-8')
        print("Browser Request:", request.split('\n')[0])

        # Parse the HTTP request line
        lines = request.split('\n')
        if len(lines) > 0 and len(lines[0].strip()) > 0:
            tokens = lines[0].split(' ')
            method = tokens[0]
            path = tokens[1] if len(tokens) > 1 else None
            print("Method:", method)
            print("Path:", path)
        else:
            print("Empty request received")
            client_socket.close()
            continue

        # Determine the requested file
        requested_file = None
        if path is not None:
            if path.startswith("/Helloworld.html"):
                requested_file = "HelloWorld.html"
            else:
                requested_file = None

        # Check if the file exists
        if not requested_file or not os.path.exists(requested_file) or os.path.isdir(requested_file):
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/plain; charset=UTF-8\r\n"
                "Content-Length: 13\r\n\r\n"
                "404 Not Found"
            )
            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()
            continue

        # Read file contents
        with open(requested_file, 'rb') as f:
            body = f.read()

        # Build HTTP response
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        )

        # Send response
        client_socket.sendall(header.encode('utf-8'))
        client_socket.sendall(body)
        client_socket.close()

if __name__ == "__main__":
    main()
