# server.py
# Name: Ehsan Ullah
# CMSID: [Your CMSID]
# Section: [Your Section]

import socket
import threading
from colorama import Fore, Style, init

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 9090

clients = {}  # socket -> username


def broadcast(message, sender_socket=None):
    """Send message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                remove_client(client)


def remove_client(client):
    """Remove client from dictionary and notify others."""
    if client in clients:
        username = clients[client]
        print(Fore.RED + f"[DISCONNECT] {username} left the chat." + Style.RESET_ALL)
        broadcast(f"[SERVER] {username} has left the chat.\n")
        del clients[client]


def handle_client(client, address):
    """Handle each client connection."""
    print(Fore.CYAN + f"[CONNECT] {address} connected." + Style.RESET_ALL)
    client.send("NICK\n".encode('utf-8'))  # <---- crucial line

    username = client.recv(1024).decode('utf-8').strip()
    while username in clients.values() or username == "":
        client.send("TAKEN\n".encode('utf-8'))
        username = client.recv(1024).decode('utf-8').strip()

    client.send("OK\n".encode('utf-8'))
    clients[client] = username

    print(Fore.GREEN + f"[JOIN] {username} joined." + Style.RESET_ALL)
    broadcast(f"[SERVER] {username} has joined the chat.\n")

    while True:
        try:
            msg = client.recv(1024).decode('utf-8').strip()
            if not msg or msg.lower() == '/quit':
                break

            if msg.startswith('@'):
                parts = msg.split(' ', 1)
                if len(parts) == 2:
                    target_user = parts[0][1:]
                    message_text = parts[1]
                    target_socket = None
                    for c, u in clients.items():
                        if u == target_user:
                            target_socket = c
                            break
                    if target_socket:
                        target_socket.send(f"[PM from {username}] {message_text}\n".encode('utf-8'))
                        client.send(f"[PM to {target_user}] {message_text}\n".encode('utf-8'))
                    else:
                        client.send(f"[SERVER] User '{target_user}' not found.\n".encode('utf-8'))
                else:
                    client.send("[SERVER] Invalid PM format. Use @username message\n".encode('utf-8'))
            else:
                broadcast(f"[{username}] {msg}\n", sender_socket=client)

        except:
            break

    remove_client(client)
    client.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(Fore.YELLOW + f"[*] Server started on {HOST}:{PORT}" + Style.RESET_ALL)

    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, address), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
