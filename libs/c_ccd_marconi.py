#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd_esopo
from c_ccd_esopo import *

#2010, eco, funciona solo con servidor nuevo, marconiServer

class CCD_MARCONI(CCD_ESOPO):
    'Clase para uso del CCD Marconi con electronica de Astronomical Researh Camera '
    def __init__(self):
		CCD.__init__(self)
		self.tipo="e2vm"
		self.label="E2V (2k x 2k) Marconi"
		self.label2="E2V-4240"
		self.xsize_total=2154
		self.ysize_total=2048
		self.xsize=self.xsize_total
		self.ysize=self.ysize_total
		self.xend=self.xsize_total
		self.yend=self.ysize_total
		self.arscale=0.1423
		self.decscale=0.1423
	
		self.usuario="Marconi_ccd class"
		self.ip="192.168.0.38"
		self.puerto=9710
		self.gain=1
		self.output=2    #Num canales de salida
		self.default_output=2    #Num canales de salida
		#control de temperaturas
		self.temp=-120.0
		self.temp_hilimit=-110
		self.temp_lowlimit=-105.0
		self.can_readtemp=True
        
############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT_4240 Marconi from Astronomical research Cameras")
        data,status=self.manda_open("INIT_MARCONI ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
	    self.mis_variables.msg_gui("SHOW_ERROR "+"Fatal Error No CCD Server Found "+data)
	    
        else:
            self.lee_MarconiServer(data)
	    data.close()
	    self.get_temp()
############################################################################

############################################################################


############################################################################

############################################################################

############################################################################

############################################################################
print "Class CCD Marconi Ready.........."