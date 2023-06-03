#!/usr/bin/env python

from  c_util import *

import sys
sys.path.append("libs")
from c_cliente import *
#V0.2 E. Colorado, Nov-2011 -> Arregle formato DEC para header
#V0.3 E. Colorado, Ene-2012 -> Use zfil lpara  formato DEC
###########################################################
class TELESCOPIO(UTIL,CLIENTE):
    'Pide estado de los telescopios en SPM'
    ar=0
    gar=0
    sar=0
    dec=0
    sdec=0
    ah_dec=0
    dec_dec=0
    ah=0
    edotel="/usr/local/instrumentacion/bin/edotel localhost 4958 2> /tmp/null"


    def __init__(self):
       pass
###########################################################
    def lee_coordenadas(self):
        #print self.edotel
        print 'leer coors'
        archivo = '/imagenes/coords.tel'

        rx=0
        try:
            #leer datos
            fo = open(archivo, "r")
            rx = fo.read();
            print "Read String is : ", rx
            # Close opend file
            fo.close()

        except:
            print 'error'
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

        self.dec=self.signo_dec+  str(self.gdec)+":"+str(self.mdec).zfill(2)+":"+str(self.sdec)

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
    def info(self):
        print "ar:", self.ar
        #print "ar segundos:", self.ar_sec
        #print "ar decimal:", self.ar_dec
        print "dec: %s, (decimal=%2.2f)" % (self.dec,self.dec_dec)
        print "ah: %s, (decimal=%2.2f)" % (self.ah,self.ah_dec)


###########################################################
    def cenit(self,espera=False):
        print "vamonos al cenit"
        data,status=self.manda("CENIT")
        if not status:
            print "bad"
            print data
            return -1

        if espera==False:
            return 0
        #esperar al cenit
        mydec= 31.0288888889
        min=mydec*0.98
        max=mydec*1.02
        print "dec, min=%d max=%d"%(min,max)


        loop=1
        loop_dec=1
        loop_ah=1
        while loop:
            time.sleep(0.5)
            self.lee_coordenadas()
            if self.ah_dec>=-0.1 and self.ah_dec<=0.11: loop_ah=0
            if self.dec_dec>=min and self.ah_dec<=max: loop_dec=0
            loop=loop_dec or loop_ar
            print "loop",loop,"loop dec",loop_dec,"loop_ah",loop_ah

        print "ya practicamente estoy en el cenit..."
        return 1

###########################################################
    def dec_offset(self,offset):
	print "Movinedo offset dec",offset
	mando="DECOF %f +D"%offset
	data,status=self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1
###########################################################
    def ar_offset(self,offset):
	print "Movinedo offset ar",offset
	mando="AROF %f +A"%offset
	data,status=self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1
############################################################################
    def mueve_tel(self, x, y):
        print "Mueve tel ", x, " ", y
        return

        if x >= 0:
            fx = 1
        else:
            fx = -1
        if y >= 0:
            fy = 1
        else:
            fy = -1

        ciclosx = int(abs(x) / 99)
        ciclosy = int(abs(y) / 99)
        print "ciclos x ", ciclosx
        print "ciclos y", ciclosy
        if ciclosx >= ciclosy:
            ciclos = ciclosx
        else:
            ciclos = ciclosy

        for i in range(0, ciclos):
            if i < ciclosx:
                mandax = 99 * fx
                datoredx = "DECOF %d +D" % (mandax)
                print datoredx
                # red_tel $datored
                self.dec_offset(mandax)
                x -= 99 * fx
                # after 2000
            if i < ciclosy:
                manday = 99 * fy
                datoredy = "AROF %d +A" % (manday)
                print datoredy
                # red_tel $datored
                self.ar_offset(manday)
                y -= 99 * fy
                # after 2000
        mandax = x
        datoredx = "DECOF %d +D" % (mandax)
        print datoredx
        self.dec_offset(mandax)
        # red_tel $datored
        # after 1000
        manday = y
        datoredy = "AROF %d +A" % (manday)
        print datoredy
        # red_tel $datored
        self.ar_offset(manday)
#a=TELESCOPIO()
#a.lee_coordenadas()
#a.info()