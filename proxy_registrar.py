#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socket
import socketserver
import sys
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


if len(sys.argv) == 2:
    config = sys.argv[1]
else:
    sys.exit("Usage: python proxy_registrar.py config")


class FicheroXML(ContentHandler):


    def __init__(self):

        self.ListaDicc = []
        self.DiccAtrib = {'server': ['name', 'ip', 'puerto'],
                          'database': ['path', 'passwpath'],
                          'log': ['path']}


    def startElement(self, name, attrs):
    
        dicc = {}
        # si existe la etiqueta en mi dicc
        if name in self.DiccAtrib:
            dicc = {'Tag': name}
            # recorre los atributos y se guardan en el dicc de tags
            for atribute in self.DiccAtrib[name]:
                dicc[atribute] = attrs.get(atribute, "")
            # guarda sin sustituir lo que ya habia dentro
            self.ListaDicc.append(dicc)

    def get_tags(self):
        # Metodo que me imprime la lista de diccionarios de tag
        return self.ListaDicc


# Parseamos y separamos el fichero en variables para poder trabajar con él
parser = make_parser()
XMLHandler = FicheroXML()
parser.setContentHandler(XMLHandler)
parser.parse(open(config))
list_XML = XMLHandler.get_tags() # XML a mi dicc
name = list_XML[0]['name']
proxy_ip = list_XML[0]['ip']
proxy_port = list_XML[0]['puerto']

# def log


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    
    dicc_rtp = {'Ip_Client':'', 'Port_CLient': 0}
    
    def handle(self):

        IP_Client = self.client_address[0]
        Port_Client = self.client_address[1]
        #print("IP: ", IP_Client)
        #print("Port: ", Port_Client)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            petc_meth = line.decode('utf-8')
            if not petc_meth:
                break
            print("El cliente nos manda: " + petc_meth)
            lista = petc_meth.split()
            print(lista)
            metodo = lista[0]
            if metodo == "REGISTER":
                address_client = lista[1].split(':')[1]
                print(address_client)
                port_client = lista[1].split(':')[2]
                print(port_client)
                expires = lista[4]
                


if __name__ == "__main__":

    serv = socketserver.UDPServer((proxy_ip, int(proxy_port)), SIPRegisterHandler)
    print("Server MiServidorBingBang listening at port 5555...")
    serv.serve_forever()
