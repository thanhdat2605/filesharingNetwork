import socket
import os
import threading
from communication import Message, MessageType, StatusCode

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #1.1 #3.1 #5.1

# Bind the socket to a specific address and port
server_address = ('localhost', 12345) #1.2 #3.2 #5.2
sock.bind(server_address) #3.3 #5.3

# Listen for incoming connections
sock.listen(1) #1.3 #3.4 #5.4

# Keep track of connected clients and their files
clients = {} #1.4 #3.5 #5.5

def handle_client(connection, client_address): #5.6
    if client_address not in clients:
        clients[client_address] = []
    try:
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            if data:
                msg = Message.deserialize_message(data.decode())
                print(f"Received {msg.type} message: {msg.content}")
                if msg.type == MessageType.REQUEST:
                    # Handle file list update
                    if 'file_list' in msg.content:
                        clients[client_address] = msg.content['file_list']
                    # Handle file request
                    elif 'file_request' in msg.content:
                        filename = msg.content['file_request']
                        file_holders = [addr for addr, files in clients.items() if filename in files]
                        response = Message(MessageType.RESPONSE, file_holders, StatusCode.OK)
                        connection.sendall(response.serialize_message().encode())
            else:
                break
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up the connection
        connection.close()

# while True: #5.7
#     # Wait for a connection
#     connection, client_address = sock.accept()
#     client_thread = threading.Thread(target=handle_client, args=(connection, client_address))
#     client_thread.start()

while True:
    # Wait for a connection #1.5 #3.6
    connection, client_address = sock.accept()
    if client_address not in clients: 
        clients[client_address] = []
    try:
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            if data:
                msg = Message.deserialize_message(data.decode())
                print(f"Received {msg.type} message: {msg.content}")
                if msg.type == MessageType.REQUEST:
                    # Store the client's files #1
                    clients[client_address] = msg.content
                    print(f"Updated file list for client {client_address}: {msg.content}")
                    # Handle file upload #1.6
                    if 'upload' in msg.content:
                        filename = msg.content['upload']
                        with open(filename, 'wb') as f:
                            file_data = connection.recv(1024)
                            while file_data:
                                f.write(file_data)
                                file_data = connection.recv(1024)
                        clients[client_address].append(filename)
                        print(f"Received file {filename} from client {client_address}")
                    # Handle file download #1.7
                    elif 'download' in msg.content:
                        filename = msg.content['download']
                        if filename in clients[client_address]:
                            with open(filename, 'rb') as f:
                                connection.sendall(f.read())
                            print(f"Sent file {filename} to client {client_address}")
                    # Handle file list update #3.7
                    if 'file_list' in msg.content:
                        clients[client_address] = msg.content['file_list']
                    # Handle file request #3.8
                    elif 'file_request' in msg.content:
                        filename = msg.content['file_request']
                        file_holders = [addr for addr, files in clients.items() if filename in files]
                        response = Message(MessageType.RESPONSE, file_holders, StatusCode.OK)
                        connection.sendall(response.serialize_message().encode())
                response = Message(MessageType.RESPONSE, "Message received", StatusCode.OK)
                connection.sendall(response.serialize_message().encode())
            else:
                break
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up the connection
        connection.close()
