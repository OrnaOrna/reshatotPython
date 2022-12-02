import socket
import threading

HOST = '127.0.0.1'
PORT = 4000
ADDRESS = (HOST, PORT)
FORMAT = 'utf-8'


class Client:
    """
    A class for a single client (server-side)
    """

    def __init__(self, sock: socket.socket):
        self.socket = sock
        self.name: str

    def handle(self):
        """
        Handles the initial connection process for the client

        :return:
        """
        pass


class Group:
    def __init__(self):
        self.participants: [Client]
        self.id: int
        self.name: str
        self.password: int


def main() -> None:
    """
    Listens for clients until terminated

    :return:
    """

    # Create the Server's socket object, and listen for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDRESS)
    server_socket.listen()

    # Print a status message
    print("Server up and running")

    while True:
        (connection, address) = server_socket.accept()

        # Print a status message
        print(f'Client connected from address #{address[0]}')

        # Handle the incoming client in a separate thread of control
        client = Client(connection)
        handler_thread = threading.Thread(target=client.handle)
        handler_thread.start()


if __name__ == '__main__':
    main()
