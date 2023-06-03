#!/usr/bin/env python

import c_filtros
from c_filtros import *
from  c_util import *
from c_cliente import *
#import time
import os.path

#V0.1, E. Colorado, Mayo 2010, incial
#V0.2, E. Colorado, Sep 2010, cambie envio de mensanjes queue tipo tupple a strings
#probado
###########################################################
class MEXMAN(UTIL,CLIENTE,FILTROS):
    'Manejo de la rueda de Filtros Mexman'
    
###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        self.archivo_filtros="filtros.cfg"
        self.mis_variables = variables
        self.numero_filtros=8
        self.extension='.cfg'
        self.usuario="mexman"
        self.filtro="no se"	#aqui estan los 2 nombres de los filtros
        self.f1=0
        self.f1_name="?"
        self.f2=0
        self.f2_name="?"
        #self.ip="192.168.0.141"
        self.ip="localhost"
        self.puerto=9706
        self.set_timeout(30)
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros Mexman",self.archivo_filtros
        
###########################################################
    def pide_posicion(self):
        if self.debug: print 'Mexman pidiendo posicion...'
        data,status=self.manda("POS")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi mexman",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def mueve_filtros(self,posicion):
        print "moviendo filtros Mexman a posicion ",posicion
        t="MOV %d "% posicion
        #t=tuple(t)
        data,status=self.manda(t)
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def procesa_respuesta(self,data):
        #'MEXMAN POS 1 vacio 16 I3\r\n'
        mando=data.split()
        key=mando[0]
        key2=mando[1]
        if key=="MEXMAN" and key2=="POS":
            if self.debug: print "llegaron filtros mexman.."
            self.f1=mando[2]
            self.f1_name=mando[3]
            self.f1=mando[4]
            self.f2_name=mando[5]
            self.filtro="%s + %s" %(self.f1_name,self.f2_name)
            if self.debug: print "el filtro es=",self.filtro
            #tupla = ["MEXMAN_UPDATE",self.filtro]
	    txt="MEXMAN_UPDATE "+self.filtro
            self.mis_variables.queue.put(txt)
############################################################################
#a=MEXMAN()

#a.pide_posicion()
#x=time.time()
#a.mueve_filtros(1)
#print "tarde seg=",time.time()-x
#a.pide_posicion()