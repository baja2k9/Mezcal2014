#!/usr/bin/env python

from  c_util import *
from c_cliente import *
import time

#poner sockectserver en programa principal y mandar datos a procesa_respuesta
#V1.0, E. Colorado, Mayo 2010, inicial

###########################################################
class SECVACIO(UTIL,CLIENTE):
    'Manejo del secundario Vacio'

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
        pass

###########################################################
    def mueve(self,posicion):

        return True
###########################################################
    def espera(self,posicion):
        pass
###########################################################
    def procesa_respuesta(self,data):

        return

############################################################################
