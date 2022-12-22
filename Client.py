import socket
import threading
from Group import Group

name = "Client"
startChat = 0

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Listening to Server and Sending Nickname
def receive():
    global name
    while True:
        try:
            # Receive Message From Server
            message = client.recv(1024).decode('ascii')
            print("MESS is: " + str(message))            # For the developer only.
            if message == 'NICK':
                # Choosing Nickname
                name = input("Choose your nickname: ")
                client.send(name.encode('ascii'))

            elif message == 'OPTIONS':
                print("<Server>")
                print("Hello client, please choose an option: ")
                print("1. Connect to a group chat.")
                print("2. Create a group chat.")
                print("3. Exit the server.")
                op = input("")
                client.send(op.encode('ascii'))

            # Option 1:
            elif message == 'OPTIONS_1_GetName':
                name = input("Please enter your name: ")
                client.send(name.encode('ascii'))
            elif message == 'OPTIONS_1_GetID':
                id = input("Please enter the group's ID: ")
                client.send(id.encode('asciii'))
            elif message == 'OPTIONS_1_GetIDError':
                print("This group ID was not found. Try again please.")
            elif message == 'OPTIONS_1_GetPass':
                password = input("Please enter the group's password: ")
                client.send(password.encode('asciii'))

            # Option 2:
            elif message == "OPTIONS_2_GetName":
                name = input("Please enter your name: ")
                client.send(name.encode('ascii'))
            elif message == 'OPTIONS_2_GetGroupName':
                groupName = input("Please enter the group's name: ")
                client.send(groupName.encode('ascii'))
            elif message == 'OPTIONS_2_GetPass':
                password = input("Please enter the group's password: ")
                client.send(password.encode('ascii'))
            elif message == 'START':
                print(name)
                write_thread = threading.Thread(target=write)
                write_thread.start()



            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occurred!")
            client.close()
            break


# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(name, input('You: '))
        client.send(message.encode('ascii'))


# Starting threads for receiving:
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# if startChat == 1:
#     write_thread = threading.Thread(target=write)
#     write_thread.start()
