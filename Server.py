import socket
import threading
import time
from Group import Group
import atexit
from typing import List

# Global connection variables
host: str = '0.0.0.0'
port: int = 33333
buffer_size = 1024

# Thread-safe event object to stop all client threads on shutdown
closed = threading.Event()

# Global list for all existing groups:
group_list: List[Group] = []


# Send all setup stuff to a connecting client. At the end, calls handle_client with the client
def setup_client(client: socket.socket):
    # Request the wanted option:
    client.send("Please choose an option between 1 and 3:\n1. Connect to a group chat.\n2. Create a group chat.\n3. Exit the server.".encode('ascii'))
    option = client.recv(buffer_size).decode('ascii')

    if option == "1":
        group_connect(client)
    elif option == "2":
        group_create(client)
    elif option == "3":
        exit_server(client)
    elif option == "":
        client.close()
    else:
        pass


# Connect a client to an existing group
def group_connect(client: socket.socket):
    # JIC the client disconnects during setup, skip everything
    disconnected: bool = False

    # Request client's name:
    client.send("Please enter your name:".encode('ascii'))
    name = client.recv(buffer_size).decode('ascii')

    # If the client has disconnected, mark it as disconnected
    if name == "":
        client.close()
        disconnected = True

    # The ID has not been found yet
    group_found: bool = False

    group_index: int = -1
    # Wait in a loop until the client supplies the ID of an existing group, or until the client disconnects
    while not group_found and not disconnected and not closed.is_set():
        # Request the group ID:
        client.send("Please enter the ID of the group you want to connect to:".encode('ascii'))
        group_id = client.recv(buffer_size).decode('ascii')

        if group_id == "":
            client.close()
            disconnected = True

        # Search for the ID the client entered in the existing IDs
        id_list: [int] = [group.id for group in group_list]

        if not disconnected:
            try:
                group_index = id_list.index(int(group_id))
            except ValueError:
                # If the client entered an invalid string
                group_index = -1
            if group_index >= 0:
                group_found = True
            else:
                client.send("Invalid group ID. Please try again.\n".encode('ascii'))

    # The password is incorrect
    correct_password = False

    # Wait in a loop until the client supplies the correct password for the group,
    # or until the client disconnects
    while not correct_password and not disconnected and not closed.is_set():
        client.send("Please enter the password for the group:".encode('ascii'))
        password = client.recv(buffer_size).decode('ascii')

        if password == "":
            client.close()
            disconnected = True

        if not disconnected:
            if group_list[group_index].password == password:
                correct_password = True
            else:
                client.send("Invalid password. Please try again.\n".encode('ascii'))

    if not disconnected:
        # Add the client to the group to the group:
        group = group_list[group_index]
        group.participant_names.append(name)
        group.member_connections.append(client)

        # Start the chat:
        client.send(f"Connected to group {group.name}".encode('ascii'))
        broadcast(f"{name} has joined the chat!", group, client, False)
        handle_client(client, group)


# Create a group with the client as first member
def group_create(client: socket.socket):
    # for error suppression only
    group_name: str = ""
    password: str = ""

    # JIC the client disconnects during setup, skip everything
    disconnected: bool = False

    # Request client's name:
    client.send("Please enter your name: ".encode('ascii'))
    name = client.recv(buffer_size).decode('ascii')

    if name == "":
        client.close()
        disconnected = True

    if not disconnected:
        # Request the new group's name:
        client.send("Please enter the group's name: ".encode('ascii'))
        group_name = client.recv(buffer_size).decode('ascii')
        if group_name == "":
            client.close()
            disconnected = True

    if not disconnected:
        client.send("Please enter the group's password: ".encode('ascii'))
        password = client.recv(buffer_size).decode('ascii')
        if password == "":
            client.close()
            disconnected = True

    if not disconnected:
        # Create an ID for the group. This will be one more than the largest
        # group ID in the existing group list
        id_list = [group.id for group in group_list]
        if len(id_list) == 0:
            new_id = 12345
        else:
            new_id = max(id_list) + 1

        # Create the new group
        group = Group(group_name, new_id, password)
        group.participant_names.append(name)
        group.member_connections.append(client)

        # Add the group to the group List
        group_list.append(group)

        # Tell the client the generated group's ID:
        client.send(f"Started group {group_name} with ID {new_id}.\n".encode('ascii'))
        client.send("Send :disconnect: or close the program to exit".encode('ascii'))

        handle_client(client, group)


# Disconnect the client from the server
def exit_server(client: socket.socket):
    client.send("Disconnected successfully.".encode('ascii'))
    client.close()



# Handling Messages From Clients
def handle_client(client: socket.socket, group: Group):
    # Repeat until the client disconnects
    disconnected: bool = False

    while not closed.is_set():
        # Receive a message from the client

        message = client.recv(buffer_size).decode('ascii')
        if message == "":
            disconnected = True
            break
        elif message == ":disconnect:":
            break
        else:
            broadcast(message, group, client, True)

    # Send to the group that the client has left
    client_index: int = group.member_connections.index(client)
    client_name: str = group.participant_names[client_index]
    broadcast(f"{client_name} has left!", group, client, False)

    # Remove the client from the group
    group.member_connections.pop(client_index)
    group.participant_names.pop(client_index)

    # If the client disconnected from the group only, return it to the menu;
    # otherwise, disconnect it entirely
    if disconnected:
        client.close()
    else:
        setup_client(client)


# Send a message to all clients in a group chat except the sending client
def broadcast(message: str, group: Group, client: socket.socket, include_name: bool):
    if include_name:
        client_index = group.member_connections.index(client)
        client_name = group.participant_names[client_index]
        for other in group.member_connections:
            if other != client:
                other.send(f"{client_name}: {message}".encode("ascii"))
    else:
        for other in group.member_connections:
            if other != client:
                other.send(f"{message}".encode("ascii"))


# Receiving / Listening Function
def receive(server: socket.socket):
    # Accept Connection
    client, address = server.accept()
    print(f"Connected with {address}")
    # Start a new thread for handling the connection
    threading.Thread(target=setup_client, kwargs={"client": client}).start()


# Graceful closing function - will definitely throw errors but whatever
def close(server: socket.socket):
    closed.set()
    # Wait a bit for all messages to be sent
    time.sleep(5)

    for group in group_list:
        for client in group.member_connections:
            client.close()
    server.close()


def main():
    # Start the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Started server at ip {socket.gethostbyname(socket.gethostname())} "
          f"and port {port}")

    closed.clear()
    atexit.register(close, server)

    # Endlessly listen for clients
    while True:
        receive(server)


if __name__ == '__main__':
    main()
