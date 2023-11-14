import socket
import os
import threading
from communication import Message, MessageType, StatusCode

def download_file(filename, other_client_address): #4.1
    other_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    other_sock.connect(other_client_address)
    message = Message(MessageType.REQUEST, {'file_request': filename}, StatusCode.OK)
    other_sock.sendall(message.serialize_message().encode())
    # Receive the file
    with open(filename, 'wb') as f:
        file_data = other_sock.recv(1024)
        while file_data:
            f.write(file_data)
            file_data = other_sock.recv(1024)
    print(f"Received file {filename} from client {other_client_address}")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #2.1 #3.1 #4.2 

# Connect the socket to the server's address and port
server_address = ('localhost', 12345) #2.2 #3.2 #4.3
try: #2.3 #3.3 #4.4
    sock.connect(server_address)
except socket.error as e:
    print(f"Could not connect to server: {e}")
    exit(1)

try:
    # Send data #1 #2.4
    files = os.listdir('.')
    message = Message(MessageType.REQUEST, files, StatusCode.OK)
    sock.sendall(message.serialize_message().encode())

    # Send file list #3.4 #4.5
    # files = os.listdir('.')
    # message = Message(MessageType.REQUEST, {'file_list': files}, StatusCode.OK)
    # sock.sendall(message.serialize_message().encode())

    # Receive response #1 #2.5 #3.6 #4.7
    data = sock.recv(16)
    response = Message.deserialize_message(data.decode())
    print(f"Received {response.type} message: {response.content}")

    # Upload a file #1.1
    filename = 'test.txt'  # replace with your file
    message = Message(MessageType.REQUEST, {'action': 'upload', 'filename': filename}, StatusCode.OK)
    sock.sendall(message.serialize_message().encode())
    with open(filename, 'rb') as f:
        sock.sendall(f.read())
    print(f"Uploaded file {filename}")

    # Download a file #1.2
    filename = 'test.txt'  # replace with your file
    message = Message(MessageType.REQUEST, {'action': 'download', 'filename': filename}, StatusCode.OK)
    sock.sendall(message.serialize_message().encode())
    with open(f'downloaded_{filename}', 'wb') as f:
        file_data = sock.recv(1024)
        while file_data:
            f.write(file_data)
            file_data = sock.recv(1024)
    print(f"Downloaded file {filename}")

    # # Request a file #3.5 #4.6
    # filename = 'test.txt'  # replace with your file
    # message = Message(MessageType.REQUEST, {'file_request': filename}, StatusCode.OK)
    # sock.sendall(message.serialize_message().encode())

    # # # Receive response
    # # data = sock.recv(16)
    # # response = Message.deserialize_message(data.decode())
    # # print(f"Received {response.type} message: {response.content}")

    # Connect to another client to download the file #3.7
    if response.content:
        other_client_address = response.content[0]  # select the first client
        other_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        other_sock.connect(other_client_address)
        message = Message(MessageType.REQUEST, {'file_request': filename}, StatusCode.OK)
        other_sock.sendall(message.serialize_message().encode())
        # Receive the file
        with open(filename, 'wb') as f:
            file_data = other_sock.recv(1024)
            while file_data:
                f.write(file_data)
                file_data = other_sock.recv(1024)
        print(f"Received file {filename} from client {other_client_address}")

    # Connect to another client to download the file #4.8
    if response.content:
        other_client_address = response.content[0]  # select the first client
        download_thread = threading.Thread(target=download_file, args=(filename, other_client_address))
        download_thread.start()

except FileNotFoundError:
    print(f"File {filename} not found.")
except socket.error as e:
    print(f"Socket error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    sock.close()