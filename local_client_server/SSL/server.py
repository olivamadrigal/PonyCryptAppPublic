#
# Team Boaz: Urian Lee, Sandhya Ramachandraiah, Mohana Gudur Valmiki, & Samira Carolina Oliva Madrigal
#
# client-server authentication using TLS
#
# References:
# https://stackoverflow.com/questions/44343230/mutual-ssl-authentication-in-simple-echo-client-server-python-sockets-ssl-m
# https://docs.python.org/3/library/socket.html
# https://docs.python.org/3/library/ssl.html
#
# OBTAIN CERTIFICATES ON TERMINAL FOR LOCAL TESTING:
# certificates USE PKI with root-CA:
# openssl ca -config etc/signing-ca.conf -in certs/localhost.csr -out certs/localhost.crt -extensions server_ext
# SAN=localhost openssl req -new -config etc/server.conf -out certs/localhost.csr -keyout certs/localhost.key
#
# X-509 self-singed:
# openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout localhost.key -out localhost.crt
#
#
# openssl help  # for overview
# openssl req ? # to view different values for an option

import socket
import ssl
import os
import pprint

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
# SELF SIGNED X509 CERTIFICATES
SERVER_CERTIFICATE = THIS_PATH + '/S/localhost.crt'
SERVER_PRIVATE_KEY = THIS_PATH + '/S/localhost.key'
CLIENT_CERTIFICATE = THIS_PATH + '/C/localhost.crt'

if __name__ == '__main__':

    """
    Server Script
    :return:
    """

    SERVER_IP = '127.0.0.1'
    PORT = 1234
    
    #  CREATE SERVER BSD SOCKET
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # https://www.gnu.org/software/libc/manual/html_node/Socket_002dLevel-Options.html
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen(10)
    
    # ACCEPT CONNECTIONS
    client, fromaddr = server_socket.accept()
    
    secure_sock = ssl.wrap_socket(client,
                                  server_side=True,
                                  ca_certs=CLIENT_CERTIFICATE, # File with CAs to verify against
                                  certfile=SERVER_CERTIFICATE,
                                  keyfile=SERVER_PRIVATE_KEY,
                                  cert_reqs=ssl.CERT_REQUIRED,
                                  ssl_version=ssl.PROTOCOL_TLSv1_2)

    peer_name = repr(secure_sock.getpeername())
    print(peer_name)
    cert = secure_sock.getpeercert()
    cipher = secure_sock.cipher()
    print(pprint.pformat(cert))
    print(cipher)
    
    # cert = secure_sock.getpeercert()
    # dict_keys(['subject', 'issuer', 'version', 'serialNumber', 'notBefore', 'notAfter'])
    # verify client
    #match = ssl.match_hostname(cert,'localhost')
    # print("match")
    # print(match)
    if not cert or ('commonName', 'localhost') not in cert['subject'][5]:
         raise Exception("ERROR")

    count = 5
    client_data_read = []
    while count:
        data = '*'.encode('utf-8')
        secure_sock.write(data)
        data = secure_sock.read(1024)
        if len(data) > 0:
            print("From client: " + data.decode('utf-8'))
        client_data_read.append(data.decode('utf-8'))
        count = count - 1

    secure_sock.close()
    server_socket.close()

