import socket
import threading
import sys
import atexit

# Global connection variables
port: int = 33333
buffer_size = 1024

# A threading event object - if the client force closes, close it
closed = threading.Event()


# Receive messages from the server and print them to the console
def receive(client: socket.socket):
    while not closed.is_set():
        message = client.recv(buffer_size).decode("ascii")
        if message == "":
            closed.set()
        else:
            print(message)


# Send messages to the server
def send(client: socket.socket):
    while not closed.is_set():
        message = input()
        if message != "":
            client.send(message.encode('ascii'))


# Graceful disconnection function
def disconnect(client: socket.socket):
    client.close()
    closed.set()


def main():
    host = sys.argv[1]
    # Connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    atexit.register(disconnect, client)

    closed.clear()

    thread1 = threading.Thread(target=receive, args=[client])
    thread2 = threading.Thread(target=send, args=[client])

    thread1.start()
    thread2.start()


if __name__ == '__main__':
    main()
