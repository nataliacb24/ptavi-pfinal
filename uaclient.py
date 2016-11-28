#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


if len(sys.argv) == 4:
    config = sys.argv[1]
    method = sys.argv[2]
    option = sys.argv[3]
else:
    sys.exit("Usage: python uaclient.py config method option")

class XMLHandler(Contenthandler):

    def __init__(self):
        self.ListaDicc = []
        self.DiccAtrib = {'account':['username', 'passwwd'],
                          'uaserver':['ip', 'puerto'],
                          'rtpaudio':['puerto'],
                          'regproxy':['ip', 'puerto'],
                          'log':['path'],
                          'audio':['path']}
    
    def startElement(self, name, attrs):
    
        dicc = {}
        dicc = {'Tag' = name}
        for atribute in self.DiccAtrib[name]
            dicc[atribute] =  attrs.get(atribute, "")
        self.ListaDicc.append()


# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP, port))

Peticion = config + " " + method + " " + option
my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)

print('Recibido -- ', data.decode('utf-8'))
datos = data.decode('utf-8').split()
if datos[1] == "100" and datos[4] == "180" and datos[7] == "200":
    Peticion = "ACK sip:" + option + "@" + IP + " SIP/2.0" + "\r\n"
    my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n')
print("Terminando socket...")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((IP, int(PORT)))
    if METODO == "register":
        PET = "REGISTER sip:" + address + ":" + port + " SIP/2.0 \r\n" + " Expires: " + option
    print("Enviando:", '\n', PET)
    my_socket.send(bytes(PET, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))

# Cerramos todo
my_socket.close()
print("Fin.")
