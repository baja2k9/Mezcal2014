#!/usr/bin/env python
# E. Colorado, mayo 2015, nueva electronica del murillito

from c_cliente import *

###########################################################
class LAMPARAS(CLIENTE):
    'Manejo de las lamparas del echelle 2015'
    
    def __init__(self,variables=None):
        self.usuario="Echelle"
        
        self.debug=False
	self.ip="192.168.0.24"
        self.puerto=2020
	self.mis_variables = variables
	self.status=''
	self.lampara='?'
	self.rendija='?'
	

###########################################################
    def estado(self):
        
	print 'echelle pidiendo estatus...'
        data,status=self.manda("ESTATUS)" )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        #print "recibi",data
	self.status=data.strip('\n')
	print 'status=',self.status,' len=',len(self.status)
	try:
	    self.saca_valores()
	except:
	    print 'no pude sacar valores de estado de echelle'
	
###########################################################
    def saca_valores(self):
	s=self.status.split("|")
	
	self.lampara=s[0].split()[1]
	self.rendija=int(s[1].split()[1])
	self.status=s[2]
	#print self.lampara,self.rendija,self.status

###########################################################
    def saca_lamparas(self):
	print 'echelle pidiendo estatus...'
        data,status=self.manda('APAGA_LAMPARA' )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        
###########################################################
    def mete_lamparas(self,pos=1):
	print 'echelle mete lampara ',pos
	#cmd='LAMPARA%d)'%(pos)
	#print cmd
        data,status=self.manda('ENCIENDE_LAMPARA' )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        
###########################################################
    def preexpone(self,tipo=None):
        print "pre expone del boller o echelle, tipo",tipo
###########################################################
    def postexpone(self):
        pass
###########################################################
    def mueve_rendija(self,pos=100):
	#ojo se tarda unos egundos en llegar
	cmd='MUEVE_RENDIJA %d'%(pos)
	print cmd
        data,status=self.manda(cmd )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
	