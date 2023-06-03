#!/usr/bin/env python

import time
import c_filtros
from c_filtros import *
from  c_util import *
from c_cliente import *
#import time
import os.path

#V0.1, E. Colorado, Oct 2010, incial


###########################################################
class SEMPOL(UTIL,CLIENTE,FILTROS):
    'Manejo delpolarizador doble sempol'
    
###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        self.mis_variables = variables
        self.numero_filtros=1
        self.usuario="polarizador sempol"
        self.ip="192.168.0.26"
        self.puerto=10001
        self.set_timeout(30)
        self.angulo=-1
        self.angulo2=-1
        #inicializar pol 1
        data,status=self.manda("?rdc \r\n")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
        else:
            self.mis_variables.mensajes(data,Color="azul")
            
        #inicializar pol 2
        time.sleep(2)
        data,status=self.manda("?rdf \r\n")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
        else:
            self.mis_variables.mensajes(data,Color="azul")
        
###########################################################
    def pide_posicion(self):
        time.sleep(2)
        if self.debug: print 'Sempol pidiendo posicion...'
        data,status=self.manda("?rdc \r\n")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        self.procesa_respuesta(data)
        
        time.sleep(2)
        data,status=self.manda("?rdf \r\n")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        self.procesa_respuesta(data)
        
        return True
###########################################################
    def mueve_pol(self,angulo,auto=True):
        print "moviendo sempol 1 a posicion ",angulo
        t="rdc %d \r\n"% angulo
        #t=tuple(t)
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        if self.debug: print "recibi",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def mueve_pol2(self,angulo,auto=True):
        print "moviendo sempol 2 a posicion ",angulo
        t="rdf %d \r\n"% angulo
        #t=tuple(t)
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        if self.debug: print "recibi",data
        self.procesa_respuesta(data)
        time.sleep(4)
        self.pide_posicion()
        return True
###########################################################
    def procesa_respuesta(self,data):
        
        #mando=data.split()
        #key=mando[0]
        #'RDC 94 13548 pour 13549\r\n\r'
        print "llego de sempol=",data
        self.mis_variables.mensajes(data)
            
            
############################################################################
#a=MEXMAN()

#a.pide_posicion()
#x=time.time()
#a.mueve_filtros(1)
#print "tarde seg=",time.time()-x
#a.pide_posicion()