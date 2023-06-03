#!/usr/bin/env python

#import time
#import os
#import gtk
#import pango
#import socket
import SocketServer
import threading 
import thread
import gobject
from subprocess import Popen, PIPE

# inicia el uso de threads
gobject.threads_init()

class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        gobject.threads_init() 
        data = self.rfile.readline().strip()
        #data = self.request.recv(1024).strip()
        foco = miApp.procesa(data)
        self.request.send(foco)

class SEC84:

    def __init__(self):
        # valores default
        self.foco = 99

    #Identifica y procesa los datos recibidos
    def procesa(self,dato):
        data = str(dato)
        bin = None
        try:
            txt = data
            if txt == "Posicion":
                self.foco+=1
                res =  "Pos "+str(self.foco)
                print   res,"+++++++++++++++++++++++++++++++++++++++++"
                return res
        except IndexError, e:
            pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 9712
    # Create the server, binding to localhost on port 9701
    SocketServer.allow_reuse_address= True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    miApp = SEC84()
    print "Escuchando en el puerto", PORT
    server.serve_forever()