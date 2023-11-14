import socket
import threading
import os
from communication import Message, MessageType, StatusCode

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP/IP

# Bind the socket to the server's address and port
server_address = ('localhost', 12345)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

connected_clients = {}
file_records = {}

def listen_for_messages(client_socket, hostname):
    while True:
        try:
            message = client_socket.recv(4096).decode()
            if message:
                print("Received message")
                message_obj = Message.deserialize_message(message)
                message_type = message_obj.type
                message_status = message_obj.status
                print(f"Message type: {message_type}")
                if message_type == "PING":
                    message_content = message_obj.content
                    if message_content == hostname and message_status == 200:
                        print(f"{hostname} is online")
                    else:
                        print(f"{hostname} is offline")
                elif message_type == "PUBLISH":
                    print("Received PUBLISH message")
                    message_content = message_obj.content
                    message_content_parts = message_content.split()
                    lname = message_content_parts[0]
                    fname = message_content_parts[1]
                    # file_path = os.path.join(lname, fname)
                    file_records[fname] = [lname, hostname]
                    # if fname in file_records:
                    #     file_records[fname].append(lname, hostname)
                    #     # file_records[fname].append(lname)
                    # else:
                    #     file_records[fname] = [lname, hostname]
                    #     # file_records[fname] = [lname]
                    print(f"Received PUBLISH message from {message_obj.content} of {hostname}")
                    print(f"File records: {file_records}")  
                elif message_type == "FETCH":
                    # Get the file name from the FETCH message
                    fname = message_obj.content
                    notification = ""
                    # Check if the file name is in the file records
                    if fname in file_records:
                        # Get the list of files with the given name
                        files = file_records[fname]
                        print(f"Files with name {fname}: {files}")
                        print(connected_clients[files[1]].getpeername())
                        notification = "1 file found" + "," + str(connected_clients[files[1]].getpeername())
                        
                    else:
                        print(f"No files named {fname} found.")
                        # numbered_list = "No files found"
                        notification = "No files found"
                        
                    message = Message(MessageType.NOTIFY, notification, StatusCode.OK)
                    client_socket.sendall(message.serialize_message().encode())
                    print("Sent notification")
                    
                    # Connect to the client with the selected file and send a SEND message
                    source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    source_sock.connect(connected_clients[files[1]].getpeername())
                    file_path = os.path.join(files[0], fname)
                    message = Message(MessageType.SEND, file_path + " " + str(client_socket.getsockname()), StatusCode.OK)
                    
                    # message = Message("SEND", selected_file[0] + " " + fname, StatusCode.OK)
                    source_sock.sendall(message.serialize_message().encode())

                    
                
                    # # Get the selected file from the file_records
                    # selected_file = file_records[int(message_obj.content)]
                    
                    # # Connect to the client with the selected file and send a SEND message
                    # source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # source_sock.connect((selected_file['hostname'], 12345))
                    # message = Message(MessageType.SEND, selected_file['lname'], StatusCode.OK)
                    # source_sock.sendall(message.serialize_message().encode())
                    
                    # # Receive the file from the client and send it to the requesting client
                    # while True:
                    #     bytes_read = source_sock.recv(4096)
                    #     if not bytes_read:
                    #         break
                    #     client_socket.sendall(bytes_read)
                    
                    # source_sock.close()
            elif message_type == "SELECT":
                # Get the selected file number from the SELECT message
                selected_file_num = int(message_obj.content)
                
                # Get the selected file from the file records
                selected_file = file_records[fname][selected_file_num]
                print(selected_file[1]) # Debugging print statement

                # Connect to the client with the selected file and send a SEND message
                source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                source_sock.connect((selected_file[1], 12345))
                file_path = os.path.join(selected_file, fname)
                message = Message("SEND", file_path + " " + str(client_socket.getsockname()), StatusCode.OK)
                
                # message = Message("SEND", selected_file[0] + " " + fname, StatusCode.OK)
                source_sock.sendall(message.serialize_message().encode())

            else:
                print("No message received or message is empty")
        except:
            print(f"Client {hostname} has disconnected")
            break

def handle_client(client_socket, hostname):
    # # Add the client socket to the list of connected clients
    # connected_clients.append(client_socket)
    try:
        connected_clients[hostname] = client_socket

        #Start listening for PUBLISH messages in a separate thread
        threading.Thread(target=listen_for_messages, args=(client_socket,hostname,), daemon=True).start()

    except client_socket in connected_clients:
        print("Client already connected")

    # # Start listening for messages in a separate thread
    # threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

def read_commands():
    while True:
        command = input('> ')
        command_parts = command.split()
        if len(command_parts) == 1:
            handle_command1(command)
        else:
            # for client_socket in connected_clients:
            handle_command2(command, client_socket)

def handle_command1(command):
    command_parts = command.split()
    if command_parts[0] == 'list':
        list_clients()
    else:
        print("Command not recognized")

def handle_command2(command, client_socket):
    command_parts = command.split()
    if command_parts[0] == 'discover':
        discover_files(command_parts[1], client_socket)
    elif command_parts[0] == 'ping':
        ping_host(command_parts[1])
    elif command_parts[0] == 'fetch':
        fetch_file(command_parts[1], client_socket)
    elif command_parts[0] == 'list':
        list_clients()
    else: 
        print("Command not recognized")

def discover_files(hostname, client_socket):
    print(f"Files of host {hostname}:")
    # for fname, record in file_records.items():
    #     if record[0] == hostname:
    #         print(fname)
    for fname in file_records:
        if hostname in file_records[fname]:
            print(fname)

    # if hostname in connected_clients:
    #     client_socket = connected_clients[hostname] 
    #     message = Message(MessageType.DISCOVER, hostname, StatusCode.OK)
    #     try:
    #         client_socket.sendall(message.serialize_message().encode())
    #         print(f"Sent DISCOVER message to {hostname}")
    #         response = client_socket.recv(4096).decode()
    #         print(f"Received response from {hostname}: {response}")
    #         if response:
    #             print(f"Files in {hostname}: {response}")
    #         else:
    #             print(f"There are no files in {hostname}'s list")
    #     except:
    #         print(f"{hostname} is offline")
    # else:
    #     print(f"{hostname} is not connected")

    # message = Message(MessageType.DISCOVER, hostname, StatusCode.OK)
    # client_socket.sendall(message.serialize_message().encode()) # instead of sock, client_socket
    # print("Sent DISCOVER message to client")  # Debugging print statement
    
    # response = client_socket.recv(4096).decode() # instead of sock, client_socket
    # print(f"Received response from client: {response}")  # Debugging print statement
    
    # if response:
    #     print(f"Files in {hostname}: {response}")
    # else:
    #     print(f"There are no files in {hostname}'s list")

def ping_host(hostname):
    if hostname in connected_clients:
        client_socket = connected_clients[hostname] 
        message = Message(MessageType.PING, hostname, StatusCode.OK)
        try:
            client_socket.sendall(message.serialize_message().encode())
            # print(f"Ping message sent to {hostname}")

            # response = client_socket.recv(4096).decode()
            # print("End response")
            # # print(f"This is the response: {response}")
            # response_obj = Message.deserialize_message(response)
            # response_content = response_obj.content
            # response_status = response_obj.status
            # # print(f"This is the response name: {response_content}")
            # # if response == StatusCode.OK:
            # if response_status == 200 and response_content == hostname:
            #     print(f"{hostname} is online")
                
            # else:
            #     print(f"{hostname} is offline.")
        except:
            print(f"{hostname} is offline")
    else:
        print(f"{hostname} is not connected")


def fetch_file(fname, client_socket):
    # Assuming that the file records are stored in a dictionary with filename as key
    if fname in file_records:
        source_clients = ','.join(file_records[fname])
        client_socket.sendall(source_clients.encode())
    else:
        client_socket.sendall('File not found'.encode())

def list_clients():
    if connected_clients:
        print("Connected clients:")
        print("------------------")
        for hostname, socket in connected_clients.items():
            print(f"Hostname: {hostname}, Peername: {socket.getpeername()}")
        # for client in connected_clients:
        #     print(client.getpeername())

    else:
        print("No clients are currently connected.")

# Start the read_commands function in a separate thread
threading.Thread(target=read_commands, daemon=True).start()

while True:
    # Wait for a connection
    print('Waiting for a connection')
    client_socket, client_address = sock.accept()
    # print (client_socket)
    print(f'connection from {client_address}')
    hostname = Message.deserialize_message(client_socket.recv(4096).decode()).content
    print(f"Connected to {hostname}")

    # Handle the client in a separate thread
    threading.Thread(target=handle_client, args=(client_socket,hostname,), daemon=True).start()

