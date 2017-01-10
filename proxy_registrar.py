#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socket
import socketserver
import sys
import os
import json
import time

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
proxy_ip = list_XML[0]['ip'] # extracción de parámetros de XML
proxy_port = list_XML[0]['puerto']

# def log


class SIPRegisterHandler(socketserver.DatagramRequestHandler):


    DiccServ = {}

    def register2json(self):
        """
        Creacion fichero json con los datos del diccionario de usuarios
        """
        json.dump(self.DiccServ, open('registered.json', 'w'))

    def json2register(self):
        """
        Comprobacion del fichero json
        """
        try:
            with open("register.json", 'r') as fichjson:
                self.DiccServ = json.load(fichjson)
        except:
            pass
            

    def delete(self):
        """
        Borrar usuarios por el tiempo de expiración
        """
        lista = []
        #print(self.DiccServ)
        for clave in self.DiccServ:
            time_now = self.DiccServ[clave][-1]
            #print(time_now)
            time_strp = time.strptime(time_now, '%Y-%m-%d %H:%M:%S')
            if time_strp <= time.gmtime(time.time()):
                lista.append(clave)
        for usuario in lista:
            del self.DiccServ[usuario]
            

    Dicc = {} # dicc de nonce
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
            #print(lista)
            metodo = lista[0]
            if metodo == "REGISTER":
                address_client = lista[1].split(':')[1]
                port_client = lista[1].split(':')[2]
                expires = lista[4]
                nonce = "89898989897898989898989"
                if len(lista) == 5:
                    time_now = int(time.time()) + int(expires)
                    time_gm = time.gmtime(time_now)
                    time_exp = time.strftime('%Y-%m-%d %H:%M:%S', time_gm)
                    self.DiccServ[address_client] = [str(IP_Client), port_client, expires,
                                                str(time_exp)]
                    Peticion = "SIP/2.0 401 Unauthorized" + "\r\n"
                    Peticion += "WWW Authenticate: Digest nonce=" + str(nonce)
                    self.wfile.write(bytes(Peticion, 'utf-8') + b"\r\n")
                    self.Dicc[address_client] = nonce
                    time_exp = time.time()
                    # log hora y evento
                    if expires == '0':
                        del self.DiccServ[address]
                if len(lista) == 8:
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    #log evento y hora
                    self.delete()
                    self.register2json()
            if metodo == "INVITE":
                #print(lista)
                address_client = lista[1].split(':')[1]
                print(self.DiccServ)


if __name__ == "__main__":

    serv = socketserver.UDPServer((proxy_ip, int(proxy_port)), SIPRegisterHandler)
    print("Server MiServidorBingBang listening at port 5555... \r\n")
    serv.serve_forever()
