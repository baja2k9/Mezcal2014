#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Enrique Colorado , inicio jueves 30 de octubre, 4:20pm
#Enrique Colorado , termine jueves 30 de octubre, 5:18pm
import sys
import os
from datetime import *
import time
import threading

import logging


import c_cliente
from c_cliente import *

import gobject
gobject.threads_init()
#################################################################################################
class SQM(CLIENTE):
    'clase para conectarse via socket tcp/ip al medidor de cielo SQM-LE'

#################################################################################################
    def __init__(self):
        print "init clase SQM"
        #self.ip='132.248.4.145'
        self.ip='192.168.0.45'
        self.puerto=10001
        self.usuario="sqm"

        self.DEBUG=False
        self.mag=-1
        self.temp=-1
        self.linea='bad'
        self.offset=0.1
        self.status=False
        self.set_timeout(1)

        #self.test()
#################################################################################################
    def read(self):
        self.status=1
        cmd='rx'
        #print 'test command',cmd
        data,status=self.manda(cmd )
        if not status:
            print "bad"
            print data
            #self.mis_variables.mensajes(data,"Log","rojo")
            self.status=-1
            return self.status
        #print "recibi",data
        self.status=self.decifra(data)
        return self.status


#################################################################################################
    def decifra(self,data):
        d=data.split(',')
        #print d
        if len(d) !=6:
            print 'Los datos no llegaron completos esta vez'
            return -1

        self.mag=d[1]
        self.mag=float(self.mag[:-1])-self.offset

        t=d[5].split()
        #print t
        #print t[0][:-1]
        self.temp=float(t[0][:-1])
        self.linea='\t%s\t%3.2f'%(self.mag,self.temp)
        return 1

#################################################################################################
    def info(self):
        print "magnitud",self.mag
        print "temp",self.temp
        print "line",self.linea
        print "status",self.status
#################################################################################################
    def test(self):
        cmd='rx'
        print 'test command',cmd
        cmd='rx'
        data,status=self.manda(cmd )
        if not status:
            print "bad"
            print data
            #self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        d=data.split(',')
        print d
#################################################################################################


#################################################################################################
s=SQM()
s.read()
s.info()

