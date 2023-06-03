#!/usr/bin/env python
from  c_util import *
from  c_telescopio import *
#V0.2 E. Colorado, Nov-2011 -> Arregle formato DEC para header
###########################################################
class TELESCOPIO15(UTIL,TELESCOPIO):
    'Pide estado de los telescopios en SPM'
    ar=0
    gar=0
    sar=0
    dec=0
    sdec=0
    ah_dec=0
    ah=0
    dec_dec=0
    edotel="/usr/local/instrumentacion/bin/edotel localhost 4958 2> /tmp/null"

    def __init__(self,variables=None):
        self.mis_variables = variables
	self.ip='192.168.0.2'
        self.puerto=4958
        self.usuario="Tel. 1.5m"
        #self.info()
###########################################################
    def lee_coordenadas(self):
        #print self.edotel
        rx=0
        try:
            rx=self.ejecuta(self.edotel)
        except:
            return False
        #print "rx=", rx
        if rx==0:
            print "error"
            return False

        data_ok=False
        datos=rx.split('\n')

        for x in datos:
            #quitar espacios en blanco iniciales
            x=x.lstrip()
            y=x.split(' ')
            if "AR"==y[0]:
                #print "y=",y
                coords= x
                data_ok=True
                #print "AR OK"

        #print "datos=", data_ok
        if not data_ok: return False
        #print "coors=",coords
        #AR  20:55:41.2 DEC -31 02'28 AH  12:34:56.7
        self.ar=coords[3:14]
        self.signo_ar=coords[3]
        self.gar=int(coords[4:6])
        self.mar=int(coords[7:9])
        self.sar=float(coords[10:14])

        #print "My AR %s %s %s" %  (self.gar , self.mar , self.sar)

        self.ar_sec=self.gar*3600*15+  self.mar*60*15+  self.sar*15
        self.ar_dec= abs(self.gar)+abs(self.mar/60.0)+abs(self.sar/3600.0)

        self.dec=coords[19:28]
        self.signo_dec=coords[19]
        self.gdec=int(coords[20:22])

        self.mdec=int(coords[23:25])
        self.sdec=float(coords[26:28])

        self.dec=self.signo_dec+  str(self.gdec)+":"+str(self.mdec)+":"+str(self.sdec)

        if self.signo_dec=="-":
            signo=-1
        else:
            signo=1
        self.dec_dec=(abs(self.gdec)+abs(self.mdec/60.0)+abs(self.sdec/3600.0))*signo

        #ah
        self.ah=coords[32:43]
        self.signo_ah=coords[32]
        self.hah=int(coords[33:35])
        self.mah=int(coords[36:38])
        self.sah=float(coords[39:43])

        #print "My AH %d %d %2.1f" %  (self.hah , self.mah , self.sah)

        if self.signo_ah=="-":
            signo=-1
        else:
            signo=1
        self.ah_dec=(abs(self.hah)+abs(self.mah/60.0)+abs(self.sah/3600.0))*signo

        return True

###########################################################
