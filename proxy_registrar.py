#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socket
import socketserver
import sys

from xml.sax import make_parse
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
parser.setContentHandler(FicheroXML)
parser.paser(open(config))
list_XML = XMLHanlder.get_tags() # XML a mi dicc
name = list_XML[0][1]['name']
ip_server = list_XML[0][1]['ip']
port_server = list_XML[0][1]['puerto']

# def log


class SIPRegisterhandler(socketserver.DatagramRequestHandler):
    
    
    def handler(self):
    
        while 1:
            line = self.rfile.read()
            petc_meth = line.decode('utf-8')
            if not petc_meth:
                break
            print("El cliente nos manda: " + petc_meth)
            lista = petc_meth.split()
            print(lista)
            metodo = lista[0]
            if metodo not in..
            elif..
            elif...
            elif...
            elif..


if __name__ == "__main__":

    serv = socketserver.UDPServer((ip_server, int(port_server)), SIPRegusterHandler)
    print("Server MiServidorBingBang listening at port 5555...")
    serv.serve_forever()
    serv.close()
