import socket
import threading
from Group import Group

# Global connection variables
host: str = '0.0.0.0'
port: int = 33333

# Global list for all existing groups:
group_list: list[Group] = []


# Sending Messages To All Connected Clients
def broadcast(message, groupID, client):
    clients = []
    print("the grouplst: ", group_list)  #
    print("\n\nbroadcast func with: (message,group_id,client): ", message, groupID, client)  #
    print("message: ", message)
    print("group_id: ", groupID)
    print("client: ", client)
    print("\n\n")  #
    for group in group_list:
        print("group.group_id is :       ", group.id)
        if int(group.id) == int(groupID):
            clients = (group.member_connections).copy()
            print("the clients: ", clients)
            try:
                clients.remove(client)
            except:
                break
            break
    print("the clients after : ", clients)
    for c in clients:
        c.send(message)


# Send all setup stuff to a connecting client. At the end, calls handle_client with the client
def setup_client(client: socket.socket):
    # Request the wanted option:
    client.send("Choose an option between 1 and 3".encode('ascii'))
    option = client.recv(1024).decode('ascii')

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

    # elif option == '2' or option == 'Client: 2':
    #
    # elif option == '3' or option == 'Client: 3':
    #     pass

    # if op == 1 or op == 2:
    #     continue
    # # Request And Store Nickname
    # client.send('NICK'.encode('ascii'))
    # nickname = client.recv(1024).decode('ascii')
    # nicknames.append(name)
    # clients.append(client)

    # Print And Broadcast Nickname
    # print("Nickname is {}".format(name))
    # broadcast("{} joined!".format(name).encode('ascii'))
    # client.send('Connected to server!'.encode('ascii'))

    # Start Handling Thread For Client
    # thread = threading.Thread(target=handle_client, args=(client, newGroup.group_id))
    # thread.start()


# Connect a client to an existing group
def group_connect(client: socket.socket):
    # JIC the client disconnects during setup, skip everything
    disconnected: bool = False

    # Request client's name:
    client.send("Enter your name".encode('ascii'))
    name = client.recv(1024).decode('ascii')

    # If the client has disconnected, mark it as disconnected
    if name == "":
        client.close()
        disconnected = True

    # The ID has not been found yet
    group_found: bool = False

    group_index: int = -1
    # Wait in a loop until the client supplies the ID of an existing group, or until the client disconnects
    while not group_found and not disconnected:
        # Request the group ID:
        client.send("Enter the ID of the group you want to connect to".encode('ascii'))
        group_id = client.recv(1024).decode('ascii')

        if group_id == "":
            client.close()
            disconnected = True

        # Search for the ID the client entered in the existing IDs
        id_list: [int] = [group.id for group in group_list]

        try:
            group_index = id_list.index(int(group_id))
        except ValueError:
            # If the client entered an invalid string
            group_index = -1
        if group_index >= 0:
            group_found = True
        else:
            client.send("Invalid group ID".encode('ascii'))

    # The password is incorrect
    correct_password = False

    # Wait in a loop until the client supplies the correct password for the group,
    # or until the client disconnects
    while not correct_password and not disconnected:
        client.send("Enter the password for the group".encode('ascii'))
        password = client.recv(1024).decode('ascii')

        if password == "":
            client.close()
            disconnected = True

        if group_list[group_index].password == password:
            correct_password = True
        else:
            client.send("Invalid password".encode('ascii'))

    if not disconnected:
        # Add the client to the group to the group:
        group = group_list[group_index]
        group.participant_names.append(name)
        group.member_connections.append(client)

        # Start the chat:
        client.send(f"Connected to group {group.name}".encode('ascii'))
        broadcast(f"{name} has joined the chat!")
        handle_client(client, group)


# Create a group with the client as first member
def group_create(client: socket.socket):
    # for error suppression only
    group_name: str = ""
    password: str = ""

    # JIC the client disconnects during setup, skip everything
    disconnected: bool = False

    # Request client's name:
    client.send("Enter your name".encode('ascii'))
    name = client.recv(1024).decode('ascii')

    if name == "":
        client.close()
        disconnected = True

    if not disconnected:
        # Request the new group's name:
        client.send("Enter the group's name".encode('ascii'))
        group_name = client.recv(1024).decode('ascii')
        if group_name == "":
            client.close()
            disconnected = True

    if not disconnected:
        client.send("Enter the group's password".encode('ascii'))
        password = client.recv(1024).decode('ascii')
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
        client.send((f"Started group {group_name} with ID {new_id}".encode('ascii'))

        handle_client(client, group)


# Disconnect the client from the server
def exit_server(client: socket.socket):
    client.send("Disconnecting...".encode('ascii'))
    client.close()


# Handling Messages From Clients
def handle_client(client: socket.socket, group: Group):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message, group, client)
        except:
            # Removing And Closing Clients
            for group in group_list:
                if client in group.member_connections:
                    index = (group.member_connections).index(client)
                    (group.member_connections).pop(index)
                    left = (group.participant_names)[index]
                    (group.participant_names).pop(index)
            client.close()
            broadcast(f'{left} left!'.encode('ascii'), group, client)
            break


# Receiving / Listening Function
def receive():
    # Accept Connection
    client, address = server.accept()
    print(f"Connected with {address}")
    # Start a new thread for handling the connection
    threading.Thread(target=setup_client, kwargs={"client": client}).start()


if __name__ == '__main__':
    # Start the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Started server at ip {socket.gethostbyname(socket.gethostname())} "
          f"and port {port}")

    # Endlessly listen for clients
    while True:
        receive()
