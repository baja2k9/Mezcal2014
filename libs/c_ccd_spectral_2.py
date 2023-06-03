#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
from c_ccd_spectral import *


class CCD_SPECTRAL_2(CCD_SPECTRAL):

    'Clase para uso del CCD 4240 con electronica de Spectral instruments #2 serie 199'

    def __init__(self):
        CCD_SPECTRAL.__init__(self)

        self.label = "E2V (2k x 2k) Spectral 2"
        print "Init Spectral 2"

        self.tipo = "SPECTRAL2"
        self.usuario = "Spectral 2 ccd class"
        self.ip = "192.168.0.18"
        #self.ip = "red0"


        self.INIT_COMMAND = "INIT_199 "
        self.INIT_MSG = "CCD INIT Series  1100, from Spectal Instruments"
        # control de temperaturas


#############################################################################

    # destrucctor
    def __del__(self):
        print "destructor de Spectral 2"
        self.manda("close ")
        self.manda("salir ")
        self.manda("SALIR ")

#############################################################################
