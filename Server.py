import socket
import threading
import time
from Group import Group

# Connection Data
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# List for groups:
groupsLst = []


# Sending Messages To All Connected Clients
def broadcast(message, group_id, client):
    clients = None
    for group in groupsLst:
        if group.groupID == group_id:
            clients = group.members.copy()
            try:
                clients.remove(client)
            except:
                break
            break
    for c in clients:
        c.send(message)


# Handling Messages From Clients
def handle(client, group_id):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message, group_id, client)
        except:
            # Removing And Closing Clients
            for group in groupsLst:
                if client in group.members:
                    index = group.members.index(client)
                    group.members.pop(index)
                    left = group.namesMem[index]
                    group.namesMem.pop(index)
            client.close()
            broadcast('{} left!'.format(left).encode('ascii'), group_id, client)
            break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request the wanted option:
        client.send("OPTIONS".encode('ascii'))
        op = client.recv(1024).decode('ascii')

        print('op is: ' + str(op))
        if op == '1' or op == 'Client: 1':
            # Request client's name:
            client.send("OPTIONS_1_GetName".encode('ascii'))
            name = client.recv(1024).decode('ascii')

            # Request group ID:
            flag = 1  # The ID was not found yet
            while flag:
                client.send("OPTIONS_1_GetID".encode('ascii'))
                time.sleep(0.1)
                group_id = client.recv(1024).decode('ascii')

                temp_id_lst = []
                for group in groupsLst:
                    temp_id_lst.append(group.groupID)
                if group_id not in temp_id_lst:
                    client.send("OPTIONS_1_GetIDError".encode('ascii'))
                    time.sleep(0.5)
                else:
                    flag = 0

            # Request password:
            client.send("OPTIONS_1_GetPass".encode('ascii'))
            password = client.recv(1024).decode('ascii')

            # Adding to the group:
            for group in groupsLst:
                if group.groupID == group_id:
                    group.namesMem.append(name)
                    group.members.appened(client)

            # Connecting to the group:
            thread = threading.Thread(target=handle, args=(client, group_id))
            thread.start()

        if op == '2' or op == 'Client: 2':
            # Request client's name:
            client.send("OPTIONS_2_GetName".encode('ascii'))
            name = client.recv(1024).decode('ascii')

            # Request the new group's name:
            client.send("OPTIONS_2_GetGroupName".encode('ascii'))
            group_name = client.recv(1024).decode('ascii')

            # Request password:
            time.sleep(0.1)
            client.send("OPTIONS_2_GetPass".encode('ascii'))
            password = client.recv(1024).decode('ascii')
            time.sleep(0.1)

            # Generate group ID:
            temp_id_lst = []
            for group in groupsLst:
                temp_id_lst.append(group.groupID)
            try:
                generate_id = max(temp_id_lst) + 1
            except:
                generate_id = 100

            # Create the group:
            new_group = Group(group_name, generate_id, password)
            new_group.namesMem.append(name)
            new_group.members.append(client)

            # Adding the group to the groups List
            groupsLst.append(new_group)

            # Tell the client the generated group's ID:
            client.send(
                ("The group: " + group_name + " constructed. It's ID is: " + str(new_group.groupID)).encode('ascii'))

            # Start the chat:
            client.send("START".encode('ascii'))

            thread = threading.Thread(target=handle, args=(client, new_group.groupID))
            thread.start()

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
        # thread = threading.Thread(target=handle, args=(client, newGroup.groupID))
        # thread.start()


receive()
