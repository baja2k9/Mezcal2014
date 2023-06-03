#!/usr/bin/env python

from  c_util import *
from c_cliente import *
import time

#poner sockectserver en programa principal y mandar datos a procesa_respuesta
#V1.0, E. Colorado, Mayo 2010, inicial

###########################################################
class SECUNDARIO(UTIL,CLIENTE):
    'Manejo del secundario del 2m,'

    usuario="Secundario 2.12m"
    foco=-1
    _error=1.0
    tipo='F/7.5'

###########################################################
    def __init__(self,variables):
        #self.ip="grulla"
        self.mis_variables = variables
        self.ip="localhost"
        self.puerto=4965
        self.puerto_respuestas=4964
###########################################################
    def pide_posicion(self):
        #print 'sec15 pidiendo posicion...'
        data,status=self.manda_sin_respuesta("posicion")
        if not status:
            print "bad"
            print data
            #self.mis_variables.mensajes(data,"Log","rojo")
            return -1

        return True

###########################################################
    def mueve(self,posicion):

        posicion*=10
        #print "Moviendo sec15 posicion ",posicion
        t="absoluto %d "% posicion
        #t=tuple(t)
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        return True
###########################################################
    def espera(self,posicion):
        a=posicion-self._error
        b=posicion+self._error
        print "Esperando secundario a posicion",posicion, "error posible=",self._error
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
        print "termine espera foco15"

###########################################################
    def procesa_respuesta(self,data):

        print "Procesando Sec 2m"
        '''
        try:
            data=data.split()
        except:
            print "No llegaron los datos completos del secundario 2m"
            return

        print data
        #-683.0 F/7.5

        try:
            self.foco=float(data[0])
        except:
            print "dato no valido del secundario 2m"

        try:
            self.tipo=data[1]
        except:
            print "Tipo de Sec no valido del secundario 2m"
        '''
        self.foco=data
        print "El foco es",self.foco
        #print "El tipo de secundario es",self.tipo

        return





############################################################################
#a=SEC84()
#c=2219
#a.pide_posicion()
#a.mueve(c)
#a.espera(c)
#a.pide_posicion()