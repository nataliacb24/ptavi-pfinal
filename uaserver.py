#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socketserver
import sys
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


if len(sys.argv) == 2:
    config = sys.argv[1]
else:
    sys.exit("Usage: python server.py config")


class FicheroXML(ContentHandler):

    def __init__(self):

        self.ListaDicc = []
        self.DiccAtrib = {'account': ['username', 'passwd'],
                          'uaserver': ['ip', 'puerto'],
                          'rtpaudio': ['puerto'],
                          'regproxy': ['ip', 'puerto'],
                          'log': ['path'],
                          'audio': ['path']}


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
# XML a mi dicc
list_XML = XMLHandler.get_tags()
#print(list_XML)
username = list_XML[0]['username']
ua_ip = list_XML[1]['ip']
ua_port = list_XML[1]['puerto']
audiortp_port = list_XML[2]['puerto']
proxy_ip = list_XML[3]['ip']
proxy_port = list_XML[3]['puerto']
fichero_audio = list_XML[5]['path']

#def log


class ServerHandler(socketserver.DatagramRequestHandler):

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
            print("Proxyregistrar nos manda: " + petc_meth)
            lista = petc_meth.split()
            #print(lista)
            metodo = lista[0]
            if metodo not in ["INVITE", "BYE", "ACK"]:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed" + b"\r\n\r\n")
                # hora y lo que ha pasado en log: enviando a
                # log
            elif metodo == "INVITE":
                self.dicc_rtp['Ip_Client'] = lista[7]
                self.dicc_rtp['Port_Client'] = lista[11]
                self.wfile.write(b"SIP/2.0 100 Trying" + b"\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ring" + b"\r\n\r\n")
                Peticion = "SIP/2.0 200 OK \r\n\r\n"
                Peticion += "Content-Type: application/sdp \r\n"
                Peticion += "v=0 \r\n" + "o=" + username + " "
                Peticion += ua_ip + "\r\n" + "s=misesion \r\n" + "t=0 \r\n"
                Peticion += "m=audio " + str(audiortp_port) + " RTP \r\n\r\n"
                self.wfile.write(bytes(Peticion, 'utf-8'))
                # hora y lo que ha pasado en log: enviando a
                # log
            elif metodo == "ACK":
                # print(self.dicc_rtp['Ip_Client'])
                # print(self.dicc_rtp['Port_Client'])
                aEjecutar = "mp32rtp -i " + self.dicc_rtp['Ip_Client'] + " -p "
                aEjecutar += self.dicc_rtp['Port_Client'] + ' < ' + fichero_audio
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
            elif metodo == "BYE":
                self.wfile.write(b"SIP/2.0 200 OK" + b"\r\n\r\n")
                # hora y lo que ha pasado en log: enviando a
                # log
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request" + b"\r\n\r\n")


if __name__ == "__main__":


    serv = socketserver.UDPServer((ua_ip, int(ua_port)), ServerHandler)
    print("Listening")
    # hora y lo que pasa en log
    # log
    serv.serve_forever()
