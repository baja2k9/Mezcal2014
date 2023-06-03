#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from datetime import *
import time
import threading

import logging


import c_cliente
from c_cliente import *

import gobject
import  json

gobject.threads_init()
#################################################################################################
class CLIMA_LOCAL(CLIENTE):
    'clase para conectarse via socket tcp/ip al medidor de clima local'

#################################################################################################
    def __init__(self):
        print "init clase CLIMA_LOCAL"
        self.ip='192.168.0.42'
        self.puerto=5555
        self.usuario="clima_local"

        self.DEBUG=False
        #{"Fecha":"2017-12-05 16:31","Humedad":25.14,"Luxes":0,"Presion":730.47,"Temperatura":6.12}

        self.fecha=''
        self.temp=0
        self.status=False
        self.set_timeout(1)
        self.hum=-1
        self.lux=-1
        self.presion=0
        self.dict=''


        #self.test()
#################################################################################################
    def read(self):
        self.status=1
        cmd='data_sen'
        #print 'test command',cmd
        data,status=self.manda(cmd )
        if not status:
            print "bad"
            print data
            #self.mis_variables.mensajes(data,"Log","rojo")
            self.status=-1
            return self.status
        #print "recibi",data
        try:
            self.status=self.decifra(data)
        except:
            print "Error al decodificar datos de clima local:",data
            self.status = -1
        return self.status


#################################################################################################
    def decifra(self,json_data):

        #print 'datos',data

        self.dict = json.loads(json_data)
        #lo de mas no es necesario
        self.temp=self.dict["Temperatura"]
        self.hum=self.dict["Humedad"]
        self.fecha = self.dict["Fecha"]
        self.lux = self.dict["Luxes"]
        self.presion = self.dict["Presion"]
        return 1

#################################################################################################
    def info(self):

        print "temp",self.temp
        print "hum",self.hum
        print "lux", self.lux
        print "fecha", self.fecha
        print "status",self.status
#################################################################################################

#################################################################################################


#################################################################################################
'''
s=CLIMA_LOCAL()
s.read()
s.info()
print '-----'
print 'temp',s.dict["Temperatura"]
'''