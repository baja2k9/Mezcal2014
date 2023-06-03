#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd
from c_ccd import *

from c_cliente import *

import c_ccd_site4
from c_ccd_site4 import *

class CCD_SITE5(CCD_SITE4):
    'Clase para uso del CCD site5 con electronica del OAN '
    def __init__(self):
        self.tam_binario=0
        CCD_SITE4.__init__(self)
        self.tipo="site5"
        self.label="site5 (1k x 1k) Oan"
        self.label2="SI03"
        self.usuario="Site5 ccd class"
        
############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT Site5 networked With OAN Electronics")
        data,status=self.manda("SI03_LIMPIA")
        
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
        
