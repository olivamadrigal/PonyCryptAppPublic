### Forked from github.
### ADAPTED by Boaz to integrate PonyCrypt
########################################################################################################
# PonyCrypt Library: creates an album                                                                  #
# Team Boaz: Urian Lee, Sandhya Ramachandraiah, Mohana Gudur Valmiki, & Samira Carolina Oliva Madrigal #
########################################################################################################
from ponycrypt import *
import socket
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptosteganography import CryptoSteganography
import os
import sys
import pyaes
import ssl
import pprint

class ChatServer:
    clients_list = []
    username_list = []   # username: list_images
    username_sock = {}
    pub_keys = {}
    username_img_idx = {}   # username: list_images
    last_received_message = ""
    MAX_BUF = 300
    THIS_PATH = os.path.dirname(os.path.realpath(__file__))
    SERVER_CERTIFICATE = THIS_PATH + '/S/localhost.crt'
    SERVER_PRIVATE_KEY = THIS_PATH + '/S/localhost.key'
    CLIENT_CERTIFICATE = THIS_PATH + '/C/localhost.crt'

    def __init__(self):
        self.pony = PonyCrypt()
        self.access_token = self.pony.get_access_token()  # FLOW CREDENTIALS
        self.chat_room_name, self.chat_room_id = self.pony.get_chat_room_id()  # CHAT ROOM & ID
        self.pony.generate_symmetric_key()
        self.CIPHER_KEY = (self.pony.CIPHER_KEY).encode('utf-8')
        self.AES = pyaes.AESModeOfOperationCTR(self.CIPHER_KEY)
        self.server_socket = None
        self.create_listening_server()

    def create_listening_server(self):
        local_ip = '127.0.0.1'
        local_port = 10319
        # CREATE SERVER BSD SOCKET
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("PonyCrypt is listening for incoming messages..")
        self.server_socket.listen(10)
        self.handle_clients()

    def receive_messages(self, so):
        while True:
            incoming_buffer = so.read(256)
            if not incoming_buffer:
                break
            str_buf = incoming_buffer.decode('utf-8')
            #str_buf = self.AES.decrypt(incoming_buffer)#.decode('utf-8')
            if 'joined:' in str_buf:
                username = str_buf.split(':')
                self.username_list.append(username[1])
                self.username_sock[so] = username[1]
                self.username_img_idx[username[1]] = 0
                self.last_received_message = str_buf #+ ' read at: ' + self.pony.CHATROOM_URL
                self.broadcast_to_all_clients(so)  # send to all clients
            else:
                if 'post' in str_buf:
                    input_buf = str_buf.split(':')
                    action = input_buf[0]
                    username = input_buf[1]
                    sender = self.username_sock[so]  # may need to update
                    data = input_buf[2]
                    # USER X HAS POSTED
                    self.username_img_idx[username] = self.username_img_idx[username] + 1
                    # THIS IS A SECRET MESSAGE
                    img_name = sender + '_' + str(self.username_img_idx[username]) + '.png'
                    self.pony.send_message(username + ':' + img_name + ':' + data, self.access_token, self.chat_room_id, img_name)

                    self.last_received_message = sender + " has posted!"  # SHARE THE URL && CRYPTO KEY
                    self.broadcast_to_all_clients(so)  # send to all clients # NOTIFY USER HAS POSTED
                else:
                    secret = self.pony.get_message(self.access_token)  # ENCRYPTED FILE BYTES
                    data = ('payload:' + secret).encode('utf-8')
                    so.write(data) #########
        so.close()

    def broadcast_to_all_clients(self, senders_socket):
        # BROADCAST TO ALL EXCEPT SENDER
        for client in self.clients_list:
            if client is not senders_socket:
                client.write(self.last_received_message.encode('utf-8'))

    def handle_clients(self):
        while True:
            client, fromaddr = self.server_socket.accept()
            # WRAP CLIENT SOCKET IN SECURE SOCKET FOR TLS
            secure_sock = ssl.wrap_socket(client,
                                          server_side=True,
                                          ca_certs=self.CLIENT_CERTIFICATE,  # File with CAs to verify against
                                          certfile=self.SERVER_CERTIFICATE,
                                          keyfile=self.SERVER_PRIVATE_KEY,
                                          cert_reqs=ssl.CERT_REQUIRED,
                                          ssl_version=ssl.PROTOCOL_TLSv1_2)

            self.add_to_clients_list(secure_sock)
            # t = threading.Thread(target=self.receive_messages, args=(secure_sock,))
            # t.start()
            print(fromaddr)
            cert = secure_sock.getpeercert()
            print(pprint.pformat(cert))
            print(secure_sock.cipher())
            if not cert or ('commonName', 'localhost') not in cert['subject'][5]:
                raise Exception("ERROR")
            # self.receive_messages()
            t = threading.Thread(target=self.receive_messages, args=(secure_sock,))
            t.start()

    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)

if __name__ == "__main__":
    ChatServer()
