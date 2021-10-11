### forked from GitHub
### ADAPTED by Boaz to integrate PonyCrypt
########################################################################################################
# PonyCrypt Library: client script                                                                     #
# Team Boaz: Urian Lee, Sandhya Ramachandraiah, Mohana Gudur Valmiki, & Samira Carolina Oliva Madrigal #
########################################################################################################

from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button
import socket
import threading
from tkinter import messagebox
import PIL.Image
import io
from base64 import *
import os
from random import randrange
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import secrets
import pytest
import pytest_html
from pathlib import Path
import shutil
# import pickle
import webbrowser
from cryptosteganography import CryptoSteganography
import base64
import pyaes
import socket
import ssl
import os
import pprint

class GUI:

    THIS_PATH = os.path.dirname(os.path.realpath(__file__))
    SERVER_CERTIFICATE = THIS_PATH + '/S/localhost.crt'
    CLIENT_PRIVATE_KEY = THIS_PATH + '/C/localhost.key'
    CLIENT_CERTIFICATE = THIS_PATH + '/C/localhost.crt'
    # INBOX = THIS_PATH + '/inbox/'   # WHERE TO DOWNLOAD IMAGES
    client_socket = None
    secure_socket = None
    last_received_message = None
    #### ISSUES TO PICKLE THESE OBJECT IFCCompression err...
    #### embed key @ clients @ server
    # RSA_PK = rsa.generate_private_key(public_exponent=257, key_size=2048, backend=default_backend())
    # RSA_PU = RSA_PK.public_key()
    # pad = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #                         algorithm=hashes.SHA256(), label=None)

    SYMMETRIC_KEY = None
    CryptoStego = None
    MAX_BUF = 300
    AES = None
    CIPHER_KEY = "This_key_for_demo_purposes_only!"

    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.get_widget = None
        self.load_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.post_button = None
        self.get_button = None
        self.rsa_button = None
        self.load_button = None
        # self.put_text_widget = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        remote_ip = '127.0.0.1'
        remote_port = 10319
        # BSD SOCK
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setblocking(True)
        # CONNECT TO SERVER
        self.client_socket.connect((remote_ip, remote_port))
        # SET SSL CONTEXT
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # CERTIFICATE IS REQUIRED FROM SERVER
        context.verify_mode = ssl.CERT_REQUIRED
        # VERIFY SERVER CERTIFICATE
        context.load_verify_locations(self.SERVER_CERTIFICATE)
        # # LOAD CHAIN OF CERTIFICATES FROM CLIENT
        context.load_cert_chain(certfile=self.CLIENT_CERTIFICATE, keyfile=self.CLIENT_PRIVATE_KEY)
        print(self.client_socket)
        if ssl.HAS_SNI:
            self.secure_socket = context.wrap_socket(self.client_socket, server_side=False, server_hostname=remote_ip)
        else:
            self.secure_socket = context.wrap_socket(self.client_socket, server_side=False)

        # GET CERTIFICATE FROM SERVER
        cert = self.secure_socket.getpeercert()
        print(cert)
        print(self.secure_socket.cipher())
        # VERIFY SERVER CERTIFICATE
        if not cert or ('commonName', 'localhost') not in cert['subject'][5]:
            raise Exception("ERROR")


    def initialize_gui(self):
        self.root.title("...~:PonyCrypt:~... ")
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_name_section()
        self.display_get_button()
        # self.display_get_text()
        # self.display_post_button()
        # self.display_get_button()
        self.display_chat_entry_box()
        self.display_load_button()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.secure_socket,))
        thread.start()
        # print("LISTENING FOR DATA")

    def receive_message_from_server(self, so):
        while True:
            buffer = so.read(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            elif "payload" in message:
                data = "NEW SECRET: " + message
                self.chat_transcript_area.insert('end', data + '\n')
                self.chat_transcript_area.yview(END)
                self.write_secrets(message)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
        so.close()
            
    def write_secrets(self, secret):
        """
         write secrets :)
        :param secret: secret
        :param file_name: filename
        """
        fp = open(self.THIS_PATH + '/client_secrets_repo.txt', 'a')
        fp.write(secret + '\n')
        fp.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_get_button(self):
        frame = Frame()
        self.post_button = Button(frame, text="GET?", width=10, command=self.on_get).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_load_button(self):
        frame = Frame()
        self.load_button = Button(frame, text="Load Pony?", width=10, command=self.on_open_uri).pack(side='right')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='PonyCrypt:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='(POST) enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    # #### TEMP
    # def display_get_text(self):
    #     frame = Frame()
    #     Label(frame, text='New secret:', font=("Serif", 12)).pack(side='top', anchor='w')
    #     frame.pack(side='top')

    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        # self.set_key()
        self.name_widget.config(state='disabled')
        message = "joined:" + self.name_widget.get()
        self.secure_socket.write(message.encode('utf-8'))

    def on_get(self):
        self.secure_socket.write(("get:" + self.name_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        action = 'post:'
        senders_name = self.name_widget.get().strip() + ":"
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (action + senders_name + data)
        self.chat_transcript_area.insert('end', message + '\n')
        self.chat_transcript_area.yview(END)
        self.secure_socket.write(message.encode('utf-8'))
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.secure_socket.close()
            exit(0)

    def on_open_uri(self):
        fp = open(self.THIS_PATH + '/uri.txt', 'r')
        uri = fp.readline()
        fp.close()
        webbrowser.open(uri)

    def set_key(self):
        fp = open(self.THIS_PATH + '/key.txt', 'r')
        self.SYMMETRIC_KEY = fp.readline()
        fp.close()
        self.CryptoStego = CryptoSteganography(self.SYMMETRIC_KEY)
        self.AES = pyaes.AESModeOfOperationCTR((self.CIPHER_KEY).encode('utf-8'))


if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
