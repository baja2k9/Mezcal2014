#!/usr/bin/env python

from c_cliente import *
###########################################################
class ECHELLE(CLIENTE):
    'Manejo de las lamparas del echelle '
    
    def __init__(self,variables=None):
        self.usuario="Echelle"
        
        self.debug=False
	self.ip="192.168.0.24"
        self.puerto=2020
	self.mis_variables = variables
	self.status=''

###########################################################
    def estado(self):
        
	print 'echelle pidiendo estatus...'
        data,status=self.manda("ESTATUS)" )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
	self.status=data.strip('\n')
	print 'status=',self.status,' len=',len(self.status)
	

###########################################################
    def saca_lamparas(self):
	print 'echelle pidiendo estatus...'
        data,status=self.manda('FUERA_LAMPARAS)' )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        
###########################################################
    def mete_lamparas(self,pos=1):
	print 'echelle mete lampara ',pos
	cmd='LAMPARA%d)'%(pos)
	print cmd
        data,status=self.manda(cmd )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        
###########################################################
    def preexpone(self):
        pass

###########################################################
    def postexpone(self):
        pass 