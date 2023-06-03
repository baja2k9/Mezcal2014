#!/usr/bin/env python

#V1.1 E. Colorado, Jun-2011 >Varios bug arreglados
#V1.2 E. Colorado, Nov-2011 -> Arregle formato DEC para header
#V1.3 E. Colorado, Ene-2012 -> Use zfil lpara  formato DEC
#V1.3 OJO REDIRECCIONE TRAFICO A PROGRAMA INTERMEDIO
from  c_telescopio import *

###########################################################
class TELESCOPIO2M(TELESCOPIO):
    'Pide estado de los telescopios en SPM'

    def __init__(self,variables=None):
        self.mis_variables = variables
        #self.edotel="/usr/local/instrumentacion/bin/edotel 192.168.0.13 4950 2> /tmp/null"
        #self.ip='192.168.0.13'
        self.ip='192.168.0.2'
        self.puerto=4950
        self.usuario="Tel. 2.12m"
        #self.set_timeout = 1

    ###########################################################
    def lee_coordenadas(self):
        for i in range(1, 3):
            #print "leyendo coor de tel 2m..., intento",i
            x=self.lee_coordenadas_una()
            if x==True:
                self.info()
                break
            else:
                rx="NO pude leer las coordenadas del TEL 2m"
                #print rx
                #self.mis_variables.mensajes(rx, "Log", "rojo")
        return x

###########################################################
    def lee_coordenadas_una(self):
        #print self.edotel
        rx=0
        try:
            data, status = self.manda("TEL")
        except:
            return False

        if not status:
            print "bad"
            print data
            return False
        #print "recibi",data
        rx=data

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
                break
            #else :
                #print "AR llego mal",datos
                

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
        #print "dec",self.dec
        self.signo_dec=coords[19]
        self.gdec=int(coords[20:22])

        self.mdec=int(coords[23:25])
        self.sdec=float(coords[26:28])

        self.dec=self.signo_dec+  str(self.gdec)+":"+str(self.mdec).zfill(2)+":"+str(self.sdec)
        #print self.dec

        if self.signo_dec=="-":
            signo=-1
        else:
            signo=1
        self.dec_dec=(abs(self.gdec)+abs(self.mdec/60.0)+abs(self.sdec/3600.0))*signo

        #ah
        self.ah=coords[32:44]
        self.signo_ah=coords[33]
        self.hah=int(coords[34:36])
        self.mah=int(coords[37:39])
        self.sah=float(coords[40:44])

        #print "My AH %d %d %2.1f" %  (self.hah , self.mah , self.sah)

        if self.signo_ah=="-":
            signo=-1
        else:
            signo=1
        self.ah_dec=(abs(self.hah)+abs(self.mah/60.0)+abs(self.sah/3600.0))*signo

        return True
###########################################################
###########################################################
    def dec_offset(self,offset):
        print "************ RUTINA Telescopio 2m ***********************"
        print "Movinedo offset dec",offset
        mando="AR_OF 0 DEC_OF %6.2f RELAD\r\n "%offset
        data,status=self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1
###########################################################
    def ar_offset(self,offset):
        print "Movinedo offset ar",offset
        mando="AR_OF %6.2f DEC_OF 0 RELAD\r\n"%offset
        data,status=self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1

'''
a=TELESCOPIO2M()
a.lee_coordenadas()
a.info()
'''
