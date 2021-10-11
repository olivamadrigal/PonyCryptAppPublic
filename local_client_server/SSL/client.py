 #
# Team Boaz: Urian Lee, Sandhya Ramachandraiah, Mohana Gudur Valmiki, & Samira Carolina Oliva Madrigal
#
# client-server authentication using TLS
#
# References:
# https://stackoverflow.com/questions/44343230/mutual-ssl-authentication-in-simple-echo-client-server-python-sockets-ssl-m
# https://docs.python.org/3/library/socket.html
# https://docs.python.org/3/library/ssl.html

import ssl
import socket
import os


THIS_PATH = os.path.dirname(os.path.realpath(__file__))
# SELF SIGNED X509 CERTIFICATES
SERVER_CERTIFICATE = THIS_PATH + '/S/localhost.crt'
CLIENT_CERTIFICATE = THIS_PATH + '/C/localhost.crt'
CLIENT_PRIVATE_KEY = THIS_PATH + '/C/localhost.key'


if __name__ == '__main__':

    SERVER_IP = '127.0.0.1'
    PORT = 1234
    
    # CREATE BSD socket interface
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(True)  # socket is in blocking mode
    # CONNECT TO SERVER
    sock.connect((SERVER_IP, PORT))
    # SET SSL CONTEXT
    # ssl.PROTOCOL_TLSv1_2 =  is the channel encryption protocol.
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # CERTIFICATE IS REQUIRED FROM SERVER
    context.verify_mode = ssl.CERT_REQUIRED
    # server_certificate = ssl.get_server_certificate((SERVER_IP, PORT))
    # VERIFY SERVER CERTIFICATE
    context.load_verify_locations(SERVER_CERTIFICATE)
    # # LOAD CHAIN OF CERTIFICATES FROM CLIENT
    context.load_cert_chain(certfile=CLIENT_CERTIFICATE, keyfile=CLIENT_PRIVATE_KEY)

    #### ca_certs = a file containing a list of root certificates.
    # IF SERVER NAME EXTENSION AVAILABLE IN API LIBRARY, SET SERVER_HOSTNAME PARAMATER
    # WRAP SOCKET IN SSL SOCKET
    print(sock)
    if ssl.HAS_SNI:
        secure_sock = context.wrap_socket(sock, server_side=False, server_hostname=SERVER_IP)
    else:
        secure_sock = context.wrap_socket(sock, server_side=False)
    
    # GET CERTIFICATE FROM SERVER
    cert = secure_sock.getpeercert()
    print(cert)
    cipher = secure_sock.cipher()
    print(cipher)

    # VERIFY SERVER CERTIFICATE
    if not cert or ('commonName', 'localhost') not in cert['subject'][5]:
        raise Exception("ERROR")

    # USER SECURE SOCKET TO READ AND WRITE DATA
    count = 5
    server_data_read = []
    while count:
        data = secure_sock.read(1024)
        server_data_read.append(data)
        if len(data) > 0:
            print("from server:" + str(data.decode('utf-8')))
        secure_sock.write('hi'.encode('utf-8'))
        count = count - 1
    secure_sock.close()
    sock.close()
