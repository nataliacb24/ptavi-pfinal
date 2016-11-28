#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handler(self):
        while 1:
        # leyendo linea a linea lo que nos envia el cliente
        Ip_client = self.cient_address[0]
        line = self.rfile.read()
        Peticion = line.decode('utf-8')
        print("El cliente nos manda " + Peticion)
        if not Peticion_SIP:
             break
        (metodo, address, sip) = Peticion.split()
            if metodo != 'REGISTER' and not "@" in address:
                break
            time_now = int(time.time()) + int(expire)
            time_gm = time.gmtime(time_now)
            time_exp = time.strftime('%Y-%m-%d %H:%M:%S', time_gm)
            if expire == '0':
                del self.Dicc[address]
            else:
                self.Dicc[address] = [str(IP_client), str(time_exp)]
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            self.delete()

        if metodo not in ["INVITE", "BYE", "ACK"]:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed" + b"\r\n" + b"\r\n")
        elif metodo == "INVITE":
            self.wfile.write(b"SIP/2.0 100 Trying" + b"\r\n" + b"\r\n")
            self.wfile.write(b"SIP/2.0 180 Ring" + b"\r\n" + b"\r\n")
            self.wfile.write(b"SIP/2.0 200 OK" + b"\r\n" + b"\r\n")
        elif metodo == "ACK":
            aEjecutar = "mp32rtp -i " + IP + " -p 23032 < " + fichero_audio
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)
        elif metodo == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK" + b"\r\n" + b"\r\n")
        else:
            self.wfile.write(b"SIP/2.0 400 Bad Request" + b"\r\n" + b"\r\n")


if __name__ == "__main__":

    if len(sys.argv) == 2:
        config = sys.argv[1]
        Port_serv = '5555'
        serv = socketserver.UDPServer(('', Port_serv), EchoHandler)
        print("Listening")
        serv.serve_forever()
    else:
        sys.exit("Usage:python uaserver.py config")
