#!/usr/bin/env python
from  c_telescopio import *

###########################################################
class TELESCOPIO1M(TELESCOPIO):
    'Pide estado de los telescopios en TONA'
    
    def __init__(self,variables=None):
        self.mis_variables = variables
	self.ip='132.248.243.4'
        self.puerto=12007
        self.usuario="Tel. 1m"
        
    def lee_coordenadas(self):
        #print self.edotel
        rx=0

        rx, s = self.manda("CT;")
        if not s:
            print "bad"
            print rx
            #self.mis_variables.mensajes(rx, "Log", "rojo")
            return False

        print "rx=", rx
        if rx==0:
            print "error"
            return False

        data_ok=False
        datos=rx.split('\n')
        
        r=str(datos)
        r=r.strip()
        print "tipo",type(r)
        
        
        #TS142338.2AH001139.2AR141159.0DC+190122AL087.246AZ090.266ET0000:
        hs = r[2:4] + ":" + r[4:6] + ":" + r[6:10]
        
        self.ar = r[24:26] + ":" + r[26:28] + ":" + r[28:32]
        
        self.dec = r[34:37] + ":" + r[37:39] + ":" + r[39:41]
        
        self.ah = r[14:16] + ":" + r[16:18] + ":" + r[18:22]
        
        
        #el = "%.3f" % float(r[42:48])
        
        #az = "%.3f" % float(r[50:57])
        
###########################################################
    def info(self):
        print "ar:", self.ar
        #print "ar segundos:", self.ar_sec
        #print "ar decimal:", self.ar_dec
        print "dec: %s" % (self.dec)
        print "ah: %s" % (self.ah)       
a=TELESCOPIO1M()
a.lee_coordenadas()
a.info()
