#!/usr/bin/env python

from  c_util import *
from c_cliente import *
import time

#V1.0, E. Colorado, Mayo 2010, inicial
###########################################################
class SEC84(UTIL,CLIENTE):
    'Manejo del secundario del 84'

    usuario="Secundario 84"
    #foco=-1
    _error=1.0
    DEBUG=False

###########################################################
    def __init__(self,variables):
        #self.ip="grulla"
        self.mis_variables = variables
        self.ip="localhost"
        self.puerto=9712
        self.foco=-1
        self.set_timeout(10)    #timeout para el secundario
###########################################################
    def pide_posicion(self):
        if self.DEBUG: print 'sec84 pidiendo posicion...'
        data,status=self.manda("Posicion")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        if self.DEBUG: print "recibi",data
        self.procesa_respuesta(data)
        return True

###########################################################
    def mueve(self,posicion):

        if self.DEBUG: print "Moviendo sec84 posicion ",posicion
        t="Mueve %d "% posicion
        #t=tuple(t)
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        #print "recibi",data
        #self.procesa_respuesta(data)
        return True
###########################################################
    def espera(self,posicion):
        a=posicion-self._error
        b=posicion+self._error
        print "esperando secundario a posicion",posicion, "error posible=",self._error
        print a,b

        conta=1
        while 1:
            time.sleep(1)
            #pedir posicion
            self.pide_posicion()
            if self.foco==posicion:
                break
            if (self.foco>=a) and (self.foco<=b):
                print "secundario ya llego",self.foco
                break
            else:
                print "secundario No ha llego",self.foco
                if conta >5:
                    self.mueve(posicion)
                    conta=1
            conta+=1
        if self.DEBUG: print "termine espera foco84"

###########################################################
    def procesa_respuesta(self,data):

        #print "procesando rx"
        mando=data.split()
        key=mando[0]
        if key=="Pos":
            self.foco=int(mando[1])
            if self.DEBUG: print "posicion sec84=",self.foco



############################################################################
#a=SEC84()
#c=2219
#a.pide_posicion()
#a.mueve(c)
#a.espera(c)
#a.pide_posicion()
