#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd_esopo
from c_ccd_esopo import *


class CCD_ESOPO_ROJO(CCD_ESOPO):
    'Clase para uso del CCD ESOPO ROJO con electronica de Astronomical Researh Camera '
    def __init__(self):
        CCD.__init__(self)
        print "Init Clase Esopo Rojo"
        self.tipo="e2ver"
        self.label="E2V (2k x 4k) Esopo Rojo"
        self.label2="E2V-4482"
        self.xsize_total=2048
        self.ysize_total=4096
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.arscale=0.2341
        self.decscale=0.2341
        self.rotate_axis=False

        self.usuario="EsopoRojo_ccd class"
        self.ip="192.168.0.37"
        self.puerto=9710
        self.gain=1

        self.output=2    #Num canales de salida
        self.n_output=2    #Num canales de salida
        self.default_output=2    #Num canales de salida
        self.output_actual=self.default_output

        self.INIT_COMMAND="INIT_ESOPOROJO "
        self.INIT_MSG="CCD INIT_4482 Esopo Rojo  from Astronomical research Cameras"

        #control de temperaturas
        self.temp=-110.0
        self.temp_hilimit=-105
        self.temp_lowlimit=-99.9
        self.can_readtemp=True

        self.extra_header=True
        self.data_cols=2048
        self.lista_data=[2048,2048,999,649,474]


############################################################################
    def update_extra_header(self):

        pass
############################################################################
