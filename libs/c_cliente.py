#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
#from socket import *
#import sys
# V1.0, E.Colorado inicial
# V1.1, E.Colorado, modifique lo del timeout, por default 0
##########################################################################


class CLIENTE:

    'clase para conectarse via socket tcp/ip'
    ip = 'localhost'
    puerto = 9725
    usuario = "para debuggear"
    __mytimeout = 0
    DEBUG = False
##########################################################################

    def __init__(self):
        print "init clase cliente "
        self.all_data_cliente=''
##########################################################################

    def manda_recibe(self, msg):
        # si ok regresa datos recividos + Status=True
        # si bad regresa error + Status=False
        self.all_data_cliente=''
        if self.DEBUG:
            print "%s --->to: %s (%d)" % (msg, self.ip, self.puerto)
        s, e = self.conecta()
        if s is None:
            return e, False

        s.send(msg + "\n")
        line = s.makefile('r', 1)
        while 1:
            data = line.readline().strip()
            try:
                txt = str(data)
                ok = True
            except:
                ok = False
            if ok:
                print "rx=", data
                self.all_data_cliente+=data+"\n"
            if not data:
                print "no mas datos"
                break
            if data == "CLOSE":
                break

        # print "lei todo red"
        line.close()
        s.close()
        if self.DEBUG:
            print 'Received', repr(data)
        return data, True
##########################################################################

    def manda_recibe_archivo(self, msg, archivo):
        # todo lo del saque va a un archivo, usado para servidor ccd oan del chava
        # si ok regresa datos  + Status=True
        # si bad regresa error + Status=False

        print "%s --->to: %s (%d) grabar archivo %s" % (msg, self.ip, self.puerto, archivo)
        s, e = self.conecta()
        if s is None:
            return e, False

        s.send(msg + "\n")

        # preparar archivo
        fileHandle = open(archivo, 'wb')
        # recibir todo
        # verificar
        while 1:
            data = s.recv(1024)
            fileHandle.write(data)
            if not data:
                break

        s.close()
        fileHandle.close()

        return data, True
##########################################################################

    def manda(self, msg):
        # si ok regresa datos recividos + Status=True
        # si bad regresa error + Status=False
        # deja cerrado el socket
        data = 'BUSY'
        mensaje=msg

        if self.DEBUG:
            print "%s --->to: %s (%d)" % (msg, self.ip, self.puerto)
        s, e = self.conecta()
        if s is None:
            return e, False

        try:
            s.send(msg + "\n")
        except socket.error, msg:
            print "Error de conexion en send", msg
        try:
            data = s.recv(1024)
        except socket.error, msg:
            print "Error de conexion en Recv", msg,mensaje, self.ip, self.puerto
        try:
            if self.DEBUG:
                print "Voy a cerrar el Socket"
            s.close()
        except socket.error, msg:
            print "Error de conexion en Close", msg

        if self.DEBUG:
            print 'Received', repr(data)
        return data, True
##########################################################################

    def manda_sin_respuesta(self, msg):
        # solo manda datos y cierra el socket
        # si ok regresa None + True
        # si bad regresa error + Status=False
        # deja cerrado el socket
        if self.DEBUG:
            print "%s --->to: %s (%d)" % (msg, self.ip, self.puerto)
        s, e = self.conecta()
        if s is None:
            return e, False
        s.send(msg + "\n")
        s.close()

        return 'None', True
##########################################################################

    def manda_open(self, msg):
        # si ok regresa datos recividos + Status=True
        # si bad regresa error + Status=False
        # deja abierto el socket
        if self.DEBUG:
            print "%s --->to: %s (%d)" % (msg, self.ip, self.puerto)
        s, e = self.conecta()
        if s is None:
            return e, False

        s.send(msg + "\n")
        return s, True
##########################################################################

    def conecta(self):

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.__mytimeout > 0:
                s.settimeout(self.__mytimeout)
                if self.DEBUG: print "conectando con timeout", self.__mytimeout

            s.connect((self.ip, self.puerto))
            return (s, True)
        except socket.error, msg:
            if self.DEBUG: print "Error de conexion", msg
            info = self.cliente_info()
            s = None
            mierror = str(msg) + " " + info
            return (s, mierror)
##########################################################################

    def cliente_info(self):
        # print "cliente info:"
        # print "Ip:",self.ip
        # print "Puerto",self.puerto
        # print "usuario",self.usuario

        txt = " =>Cliente info: IP:" + self.ip + " Puerto:" + \
            str(self.puerto) + " usuario:" + self.usuario
        if self.DEBUG: print txt
        return txt
##########################################################################

    def set_timeout(self, tiempo):
        self.__mytimeout = tiempo
##########################################################################
# a=CLIENTE()
#d,s=a.manda_recibe("LEE_TEMP ")
# print "data",d
# print "status",s
