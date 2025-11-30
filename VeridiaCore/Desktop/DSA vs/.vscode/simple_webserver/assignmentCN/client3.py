# client.py
# Name: Ehsan Ullah
# CMSID: [Your CMSID]
# Section: [Your Section]

import socket
import threading
from colorama import Fore, Style, init

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 9090


def receive_messages(sock):
    """Continuously receive messages from server."""
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                print(Fore.RED + "[SERVER] Disconnected." + Style.RESET_ALL)
                break

            if msg.strip() == 'NICK':
                continue  # handled in main thread
            elif msg.strip() == 'TAKEN':
                continue
            elif msg.strip() == 'OK':
                continue
            else:
                print(Fore.CYAN + msg.strip() + Style.RESET_ALL)

        except:
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Wait for NICK request
    msg = sock.recv(1024).decode('utf-8').strip()
    if msg == 'NICK':
        username = input(Fore.YELLOW + "Enter your username: " + Style.RESET_ALL)
        sock.send(username.encode('utf-8'))

        response = sock.recv(1024).decode('utf-8').strip()
        while response == 'TAKEN':
            username = input(Fore.RED + "Username taken, try again: " + Style.RESET_ALL)
            sock.send(username.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8').strip()

        print(Fore.GREEN + f"Welcome, {username}! Type /quit to exit." + Style.RESET_ALL)

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        message = input()
        if message.lower() == '/quit':
            sock.send(message.encode('utf-8'))
            break
        sock.send(message.encode('utf-8'))


if __name__ == "__main__":
    main()
