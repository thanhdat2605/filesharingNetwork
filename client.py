import socket
import threading
import os
from communication import Message, MessageType, StatusCode

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('localhost', 12345)
try:
    sock.connect(server_address)
except socket.error as e:
    print(f"Could not connect to server: {e}")
    exit(1)


def handle_client(client_sock):
    # This function will be run in a separate thread for each client
    while True:
        message = sock.recv(4096).decode()
        print("Received message")
        # print(message)
        handle_message(message, sock)
        break
    client_sock.close()
    #     data = client_sock.recv(1024)
    #     if not data:
    #         break
    #     print(f"Received data: {data}")
    #     client_sock.sendall(data)  # Echo the data back to the client
    # client_sock.close()

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(sock.getsockname())
    server_sock.listen(1)

    while True:
        client_sock, client_address = server_sock.accept()
        print(f"Accepted connection from {client_address}")

        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))
        client_thread.start()

#Start listening
threading.Thread(target=start_server, daemon=True).start()

def handle_message(message, sock):
    # print("Already in handle_message")
    message_obj = Message.deserialize_message(message)
    message_type = message_obj.type
    # print(f"Message type: {message_type}")
    if message_type == "PING":
        print("Received PING")
        response = Message(MessageType.PING, name, StatusCode.OK)
        sock.sendall(response.serialize_message().encode())
        print('Sent ping response')
    elif message_type == "SEND":
        # Split the message content into the file path and client socket
        file_path, client_socket_str = message_obj.content.split(" ")
        
        # Parse the client socket string into a tuple
        client_socket = tuple(client_socket_str.strip('()').split(','))
        
        # Connect to the client socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(client_socket)
        
        # Read the file and send it to the client
        with open(file_path, 'rb') as file:
            # data = file.read()
            # client_sock.sendall(data)
            while True:
                bytes_read = file.read(4096)
                if not bytes_read:
                    break
                client_sock.sendall(bytes_read)
        
        print(f"Sent file {file_path} to client {client_socket}")
    elif message_type == "NOTIFY":
        message, client_socket_adr = message_obj.content.split(',', 1)

        # Print the message
        print(message)
        print(client_socket_adr)
        # # Parse the client address string into a tuple
        # client_address = client_address_str.strip('()').split(':')
        # client_address = (client_address[0], int(client_address[1]))
        # Connect to the client and receive the file
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(client_socket_adr)

        with open('received_file', 'wb') as file:
            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                file.write(data)

        print(f"Received file from client {client_socket_adr}")
        # # Split the content into two parts
        # parts = message_obj.content.split(' ', 1)
        # print(parts[0])  # Print the first part

        # # Use the second part as the address to connect to the other client
        # address = parts[1].strip().split(':')
        # host = address[0]
        # port = int(address[1])

        # # Create a client socket to connect to the other client
        # client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_sock.connect((host, port))

        # # Receive the file from the other client and save it to disk
        # with open('received_file', 'wb') as file:
        #     while True:
        #         data = client_sock.recv(4096)
        #         if not data:
        #             break
        #         file.write(data)
    
    elif message_type == "SELECTFROM":
        print("Received SELECTFROM message")
        print(message_obj.content)
        if message_obj.content != "No files found":
            print("Executing if statement")
            # Ask the user to select a file
            print("Enter 'select num' to select a file: ")
            selection = input()
            print(f"Selection: {selection}")
            # Send a SELECT message to the server with the selected file
            message = Message(MessageType.SELECT, selection.split(' ')[1], StatusCode.OK)
            sock.sendall(message.serialize_message().encode())
            # sock.sendall(selection.split(' ')[1].encode())  

            # Receive the file from the server and save it to the local repository
            with open(fname, 'wb') as file:
                while True:
                    bytes_read = sock.recv(4096)
                    if not bytes_read:
                        break
                    file.write(bytes_read) 

            print(f"File {fname} fetched")
        else:
            print("No files found")

    else:
        print("Don't match any message")

def listen_for_messages(sock):
    # while True:
    #     data = sock.recv(4096).decode()
    #     messages = data.split('\n')
    #     for message in messages:
    #         if message:
    #             handle_message(message, sock)
    while True:
        message = sock.recv(4096).decode()
        print("Received message")
        # print(message)
        handle_message(message, sock)

# Start listening for messages in a separate thread
threading.Thread(target=listen_for_messages, args=(sock,), daemon=True).start()


# Send a CONNECT message with the client's name
name = input('Enter your name: ')
message = Message(MessageType.REQUEST, name)
sock.sendall(message.serialize_message().encode())

def handle_command(command):
    # while True:
    #     command = input('> ')
        command_parts = command.split()
        if command_parts[0] == 'publish':
            publish_file(command_parts[1], command_parts[2])
        elif command_parts[0] == 'fetch':
            # fetch_thread = threading.Thread(target=fetch_file, args=(command_parts[1],))
            # fetch_thread.start()
            fetch_file(command_parts[1])
        elif command_parts[0] == 'hello':
            print("Hello")
        else:
            print("Command not recognized")

def publish_file(lname, fname):
    if os.path.isdir(lname):
        # Create the full path to the file
        file_path = os.path.join(lname, fname)
        if os.path.isfile(file_path):

            message_content = f"{lname} {fname}"
            message = Message(MessageType.PUBLISH, message_content, StatusCode.OK)
            
            # Send the message to the server
            sock.sendall(message.serialize_message().encode())
            
            # # Send the file to the server
            # with open(lname, 'rb') as f:
            #     while True:
            #         bytes_read = f.read(4096)
            #         if not bytes_read:
            #             break
            #         sock.sendall(bytes_read)
        else:
            print(f"File {fname} does not exist in {lname}")
    else:
        print(f"Repository {lname} is invalid")

def fetch_file(fname):
    # Send a FETCH message to the server
    message = Message(MessageType.FETCH, fname, StatusCode.OK)
    sock.sendall(message.serialize_message().encode())
    
    # # Wait for a SELECTFROM message from the server
    # response = sock.recv(4096).decode()
    # message_obj = Message.deserialize_message(response)
    # print("Received response")
    # # print(message_obj.content)
    # if message_obj.content != "No files found":
    #     # Ask the user to select a file
    #     selection = input("Enter 'select num' to select a file: ")
        
    #     # Send a SELECT message to the server with the selected file
    #     # message = Message(MessageType.SELECT, selection.split(' ')[1], StatusCode.OK)
    #     # sock.sendall(message.serialize_message().encode())
    #     sock.sendall(selection.split(' ')[1].encode())  

        # # Receive the file from the server and save it to the local repository
        # with open(fname, 'wb') as file:
        #     while True:
        #         bytes_read = sock.recv(4096)
        #         if not bytes_read:
        #             break
        #         file.write(bytes_read) 

        # print(f"File {fname} fetched")


    # # Receive the numbered list of hostnames and directories from the server
    # response = sock.recv(4096).decode()
    # source_clients = response.split(',')
    
    # # Print the numbered list and ask the user to select a file
    # print("Please select a file:")
    # for i, source_client in enumerate(source_clients):
    #     print(f"{i}: {source_client}")
    # selection = input("Enter the number of the file you want to fetch: ")
    
    # # Send a SELECT message to the server with the selected file
    # message = Message(MessageType.SELECT, selection, StatusCode.OK)
    # sock.sendall(message.serialize_message().encode())
    
    # # Receive the file from the server and save it to the local repository
    # with open(fname, 'wb') as f:
    #     while True:
    #         bytes_read = sock.recv(4096)
    #         if not bytes_read:
    #             break
    #         f.write(bytes_read)

    
    # message = Message(MessageType.FETCH, fname, StatusCode.OK)
    # sock.sendall(message.serialize_message().encode())
    
    # response = sock.recv(4096).decode()
    # source_clients = response.split(',')
    
    # # Select a source client. This can be random or based on some criteria.
    # source_client = source_clients[0]
    
    # # Connect to the source client and fetch the file
    # source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # source_sock.connect((source_client, 12345))
    
    # message = Message(MessageType.FETCH, fname, StatusCode.OK)
    # source_sock.sendall(message.serialize_message().encode())
    
    # with open(fname, 'wb') as f:
    #     while True:
    #         bytes_read = source_sock.recv(4096)
    #         if not bytes_read:
    #             break
    #         f.write(bytes_read)
    
    # source_sock.close()

# Start the read_commands function in a separate thread
# threading.Thread(target=handle_command, daemon=True).start()

while True:
    command = input('> ')
    if command:
        handle_command(command)

# while True:
#     command = input('> ')
#     command_thread = threading.Thread(target=handle_command, args=(command,))
#     command_thread.start()

# def handle_command(command):
#     command_parts = command.split()
#     if command_parts[0] == 'publish':
#         publish_file(command_parts[1], command_parts[2])
#     elif command_parts[0] == 'fetch':
#         fetch_file(command_parts[1])