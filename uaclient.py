#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import time

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


if len(sys.argv) == 4:
    config = sys.argv[1]
    metodo = sys.argv[2]
    option = sys.argv[3]
else:
    sys.exit("Usage: python uaclient.py config method option")


class FicheroXML(ContentHandler):
    """
    Se crea el fichero XML
    """

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
        # Metodo que me imprime la lista de diccionarios de tags
        return self.ListaDicc

# parseamos y separamos el fichero para poder trabajar con él
parser = make_parser()
XMLHandler = FicheroXML()
parser.setContentHandler(XMLHandler)
parser.parse(open(config))
list_XML = XMLHandler.get_tags()
# extracción de parámetros de fichero XML
username = list_XML[0]['username']
ua_ip = list_XML[1]['ip']
ua_port = list_XML[1]['puerto']
audiortp_port = list_XML[2]['puerto']
proxy_ip = list_XML[3]['ip']
proxy_port = list_XML[3]['puerto']
fichero_audio = list_XML[5]['path']
fichlog = list_XML[4]['path']

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Conectando con proxy
my_socket.connect((proxy_ip, int(proxy_port)))


def log(formato, hora, evento):
    fich_log = open(fichlog, 'a')
    formato = '%Y%m%d%H%M%S'
    hora = time.gmtime(hora)
    forma_hora = fich_log.write(time.strftime(formato, hora))
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()


# Si recibimos una cosa u otra
if metodo == "REGISTER":
    Peticion = metodo + " sip:" + username + ":" + ua_port
    Peticion += " SIP/2.0" + "\r\n" + "Expires: " + option + "\r\n"
    #log evento y hora
    hour = time.time()
    event = " Sent to " + proxy_ip + ':' + str(proxy_port) + ':'
    event += Peticion
    log('', hour, event)
    print("Enviando: ", Peticion)
    my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n\r\n')
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))
    datos_rcv = data.decode('utf-8').split()
    if datos_rcv[1] == "401":
        Peticion = metodo + " sip:" + username + ":" + ua_port
        Peticion += " SIP/2.0" + "\r\n" + "Expires: " + option + "\r\n"
        Peticion += "Authorization: Digest response="
        Peticion += "123123212312321212123 \r\n"
        print("Enviando: ", Peticion)
        my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n\r\n')
        #log evento y hora
        hour = time.time()
        event = " Sent to " + proxy_ip + ':' + str(proxy_port) + ':'
        event += Peticion
        log('', hour, event)
        data = my_socket.recv(int(proxy_port))
        datos_rcv = data.decode('utf-8').split()

elif metodo == "INVITE":
    Peticion = metodo + " sip:" + option + " SIP/2.0 \r\n\r\n"
    Peticion += "Content-Type: application/sdp \r\n"
    Peticion += "v=0 \r\n" + "o=" + username + " " + ua_ip + "\r\n"
    Peticion += "s=misesion \r\n" + "t=0 \r\n"
    Peticion += "m=audio " + audiortp_port + " RTP \r\n\r\n"
    #log evento y hora
    hour = time.time()
    event = " Sent to " + proxy_ip + ':' + str(proxy_port) + ':'
    event += Peticion
    log('', hour, event)
    print("Enviando: ", Peticion)
    my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))
    datosrcv = data.decode('utf-8').split()
    if datosrcv[1] == "100" and datosrcv[4] == "180" and datosrcv[7] == "200":
        metodo = "ACK"
        Ip_Serv = datosrcv[13]
        Port_Serv = datosrcv[17]
        Peticion = metodo + " sip:" + option + " SIP/2.0 \r\n"
        print("Enviando: ", Peticion)
        my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n')
        aEjecutar = "mp32rtp -i " + Ip_Serv + " -p " + Port_Serv + ' < '
        aEjecutar += fichero_audio
        print("Vamos a ejecutar", aEjecutar)
        os.system(aEjecutar)
        #log evento y hora
        hour = time.time()
        event = " Sent to " + proxy_ip + ':' + str(proxy_port) + ':'
        event += Peticion
        log('', hour, event)

elif metodo == 'BYE':
    Peticion = metodo + " sip:" + option + " SIP/2.0 \r\n\r\n"
    print("Enviando: ", Peticion)
    my_socket.send(bytes(Peticion, 'utf-8') + b'\r\n\r\n')
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))
    datos_rcv = data.decode('utf-8').split()
    #log evento y hora
    hour = time.time()
    event = " Sent to " + proxy_ip + ':' + str(proxy_port) + ':'
    event += Peticion
    log('', hour, event)


# Cerramos todo
print("terminando socket...")
my_socket.close()
print("Fin.")
# hora y lo que pasa en el log
# log
