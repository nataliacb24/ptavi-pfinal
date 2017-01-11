#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socket
import socketserver
import sys
import os
import json
import time
import hashlib

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
fichlog = list_XML[2]['path']


def log(formato, hora, evento):
    fich_log = open(fichlog, 'a')
    formato = '%Y%m%d%H%M%S'
    hora = time.gmtime(hora)
    forma_hora = fich_log.write(time.strftime(formato, hora))
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()


#def password(dircc_user):
#    fich = open("passwords")
#    datos = fich.readlines()
#    for linea in datos:
#        if linea != "":
#            user = linea.split(" ")
#           if user[0] == dircc_user:
#              passwd = user[1]
# return passwd


class SIPRegisterHandler(socketserver.DatagramRequestHandler):


    DiccUser = {}

    def register2json(self):
        """
        Creacion fichero json con los datos del diccionario de usuarios
        """
        json.dump(self.DiccUser, open('registered.json', 'w'))

    def json2register(self):
        """
        Comprobacion del fichero json
        """
        try:
            with open("register.json", 'r') as fichjson:
                self.DiccUser = json.load(fichjson)
        except:
            pass
            

    def delete(self):
        """
        Borrar usuarios por el tiempo de expiración
        """
        lista = []
        #print(self.DiccUser)
        for clave in self.DiccUser:
            time_now = self.DiccUser[clave][-1]
            #print(time_now)
            time_strp = time.strptime(time_now, '%Y-%m-%d %H:%M:%S')
            if time_strp <= time.gmtime(time.time()):
                lista.append(clave)
        for usuario in lista:
            del self.DiccUser[usuario]
            print('Borrando', usuario)
            

    Dicc = {} # diccionario de nonce
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
                    self.DiccUser[address_client] = [str(IP_Client),
                                                     port_client, expires,
                                                     str(time_exp)]
                    Peticion = "SIP/2.0 401 Unauthorized" + "\r\n"
                    Peticion += "WWW Authenticate: Digest nonce=" + str(nonce)
                    self.wfile.write(bytes(Peticion, 'utf-8') + b"\r\n")
                    self.Dicc[address_client] = nonce
                    # log hora y evento
                    hour = time.time()
                    event = "Sent to " + IP_Client + ':' + str(Port_Client)
                    event += ':' + Peticion + '\r\n'
                    log('', hour, event)
                    if expires == '0':
                        del self.DiccUser[address_client]
                if len(lista) == 8:
                    #contr = password(address_client)
                    #contr = contr[:-1]
                    #Autoriza = lista[7].split("=")[1]
                    #nonce = self.Dicc[address_client]
                    #nonce_bytes = bytes(str(nonce), 'utf-8')
                    #contrsñ = bytes(contr, 'utf-8')
                    #m = hashlib.md5()
                    #m.update(contrsñ + nonce_bytes)
                    #response = m.hexdigest()
                    #if response == Autoriza:
                    self.wfile.write(b"SIP/2.0 200 OK" + b"\r\n\r\n")
                    #log evento hora
                    hour = time.time()
                    event = "Sent to " + IP_Client + ':' + str(Port_Client)
                    event += ':' + "SIP/2.0 200 OK" + '\r\n'
                    log('', hour, event)
                    self.delete()
                    self.register2json()
                    
            elif metodo == "INVITE" or "BYE":
                self.register2json()
                address_client = lista[1].split(':')[1]
                #print(self.DiccUser)
                if address_client in self.DiccUser.keys():
                    ua_ip = self.DiccUser[address_client][0]
                    ua_port = int(self.DiccUser[address_client][1])
                    # Creamos socket, lo configuramos
                    # y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((ua_ip,
                                       int(ua_port))) #conectando con uasever(leo)
                    my_socket.send(bytes(petc_meth, 'utf-8') + b'\r\n\r\n')
                    data = my_socket.recv(ua_port)#leonard
                    print(data.decode('utf-8'))
                    self.wfile.write(bytes(data.decode('utf-8'),
                                     'utf-8') + b'\r\n')
                    #log evento y hora
                    hour = time.time()
                    event = "Received from " + ua_ip + ':' + str(ua_port)
                    event += ':' + data.decode('utf-8') + '\r\n'
                    log('', hour, event)
                    hour = time.time()
                    event = " Sent to " + IP_Client + ':' + str(Port_Client)
                    event += ':' + data.decode('utf-8') + '\r\n'
                    log('', hour, event)
                else:
                    #usuario no encontrado
                    self.wfile.write(b"SIP/2.0 404 User Not Found" + b"\r\n")
                    #log evento y hora
                    hour = time.time()
                    event = " Sent to " + IP_Client + ':' + str(Port_Client)
                    event += ':' + "SIP/2.0 404 User Not Found" + '\r\n'
                    log('', hour, event)
            elif metodo == "ACK":
                address_client = lista[1].split(':')[1]
                if address_client in self.DiccUser:
                    ua_ip = self.DiccUser[address_client][0]
                    ua_port = int(self.DiccUser[address_client][1])
                    # Creamos socket, lo configuramos
                    # y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((ua_ip,
                                       int(ua_port))) #conectando con uasever(leo)
                    my_socket.send(bytes(petc_meth, 'utf-8') + b'\r\n\r\n')
                    data = my_socket.recv(Port_Client)#leonard
                    self.wfile.write(bytes(data.decode('utf-8'),
                                     'utf-8') + b'\r\n')
                    #log evento y hora
                    hour = time.time()
                    event = " Received from " + IP_Client + ':' + str(Port_Client)
                    event += ':' + data.decode('utf-8') + '\r\n'
                    log('', hour, event)
            elif metodo not in ["INVITE", "BYE", "ACK"]:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed"
                                 + b"\r\n\r\n")
                #log evento y hora
                hour = time.time()
                event = " Sent to " + IP_Client + ':' + str(Port_Client)
                event += ':' + "SIP/2.0 404 User Not Found" + '\r\n'
                log('', hour, event)


if __name__ == "__main__":

    serv = socketserver.UDPServer((proxy_ip, int(proxy_port)),
                                   SIPRegisterHandler)
    print("Server MiServidorBingBang listening at port 5555... \r\n")
    serv.serve_forever()
