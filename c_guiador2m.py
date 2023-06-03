#!/usr/bin/env python
import sys
import time

sys.path.append("libs")
from c_cliente import *

###########################################################
class GUIADOR(CLIENTE):
    'Manejo del guiador del 2m'

###########################################################
    def __init__(self,variables):
        CLIENTE.__init__(self)

        self.ip="192.168.0.2"
        self.puerto=4996
        #self.set_timeout(15)
        self.usuario='Guiador2m'
        #manda_mensaje_al_guiador "no_guia1"
        #manda_mensaje_al_guiador "guia"
        #manda_mensaje_al_guiador "no_guia2"
