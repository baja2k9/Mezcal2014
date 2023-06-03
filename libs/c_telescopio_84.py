#!/usr/bin/env python

from  c_util import *
import time
import sys
sys.path.append("libs")
from c_cliente import *

#V0.2 E. Colorado, Nov-2011 -> Arregle formato DEC para header
#V0.3 E. Colorado, Ene-2012 -> Use zfil lpara  formato DEC
#V0.4 E. Colorado, Oct-2017 -> Nueva consola, cambio signo offset AR y esta ens seg, de tiempo
###########################################################
class TELESCOPIO84(UTIL,CLIENTE):
    'Pide estado de los telescopios en SPM'
    ar=0
    gar=0
    sar=0
    dec=0
    sdec=0
    ah_dec=0
    dec_dec=0
    ah=0

###########################################################
    def __init__(self,variables=None):
        self.mis_variables = variables

        self.ip = '192.168.0.10'
        self.puerto = 4955
        self.usuario = "Tel. 84"
###########################################################
    def lee_coordenadas(self):

        rx=0
        try:
            data, status = self.manda("TEL")
        except:
            return False

        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return False
        #print "recibi",data
        rx=data
        #print "rx=", rx
        if rx==0:
            print "error"
            return False

        data_ok=False
        datos=rx.split('\n')
        datos=''.join(datos)
        print 'llego de tel',datos

        #['AhG  2.178686 DeCG 8.756805 AH +02:10:43.27 DEC +08:45:24.50 AR 19:50:55.97 CA_AHD 0.0 ESTADO_G 0  TS 22:01:39.24']OK

        i=datos.find('AR')
        if i:
            #sacar ar
            data_ok = True
            ar=datos[i+2:]
            ar=ar.split()
            #print 'aqui',ar
            self.ar=ar[0]
            a=ar[0].split(':')
            print 'ar',a

            self.gar = int(a[0])
            self.mar = int(a[1])
            self.sar = float(a[2])

            self.ar_sec = self.gar * 3600 * 15 + self.mar * 60 * 15 + self.sar * 15
            self.ar_dec = abs(self.gar) + abs(self.mar / 60.0) + abs(self.sar / 3600.0)
            #print 'ar dec',self.ar_dec
        else:
            data_ok = False
            return False

        i = datos.find('DEC')
        if i:
            dec=datos[i+4:]
            #print 'dec', dec
            a = dec.split()
            self.dec=a[0]
            a=a[0].split(':')
            print 'dec', a

            self.signo_dec=a[0][0]
            print 'signo dec',self.signo_dec

            self.gdec=int(a[0])
            self.mdec=int(a[1])
            self.sdec=float(a[2])

            #self.dec=self.signo_dec+  str(self.gdec)+":"+str(self.mdec).zfill(2)+":"+str(self.sdec)
            #self.dec = str(self.gdec) + ":" + str(self.mdec).zfill(2) + ":" + str(self.sdec)

            if self.signo_dec=="-":
                signo=-1
            else:
                signo=1
            self.dec_dec=(abs(self.gdec)+abs(self.mdec/60.0)+abs(self.sdec/3600.0))*signo
            self.dec_sec =self.dec_dec*3600

        #ah
        i = datos.find('AH')
        if i:
            ah = datos[i + 3:]
            a = ah.split()
            self.ah = a[0]
            a = a[0].split(':')
            print 'ah',a

            self.signo_ah=a[0][0]
            print 'signo ah',self.signo_ah

            self.hah=int(a[0])
            self.mah=int(a[1])
            self.sah=float(a[2])
            #print "My AH %d %d %2.1f" %  (self.hah , self.mah , self.sah)
            if self.signo_ah=="-":
                signo=-1
            else:
                signo=1
            self.ah_dec=(abs(self.hah)+abs(self.mah/60.0)+abs(self.sah/3600.0))*signo
            print 'ah_dec',self.ah_dec

        return True
###########################################################
    def info(self):
        print "ar:", self.ar
        #print "ar segundos:", self.ar_sec
        #print "ar decimal:", self.ar_dec
        print "dec: %s, (decimal=%2.4f)" % (self.dec,self.dec_dec)
        print "ah: %s, (decimal=%2.4f)" % (self.ah,self.ah_dec)


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
        conta_e=0
        while loop:
            time.sleep(0.5)
            e=self.lee_coordenadas()
            if not e:
                conta_e+=1
            if conta_e >10:
                txt= 'ERROR, NO PUEDO LEER LA CONSOLA'
                print txt
                self.mis_variables.mensajes(txt, "Log", "rojo")
                break
            if self.ah_dec>=-0.1 and self.ah_dec<=0.11: loop_ah=0
            if self.dec_dec>=min and self.ah_dec<=max: loop_dec=0
            loop=loop_dec or loop_ah
            print "loop",loop,"loop dec",loop_dec,"loop_ah",loop_ah

        self.mis_variables.mensajes("ya practicamente estoy en el cenit...", "Log", "green")
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
        #OJO por cambio de consola offset va en segundos de tiempo
        offset=offset*-1/15.0
        print "Cambie signo offset ar por consola nueva", offset

        mando="AROF %f +A"%offset
        data,status=self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1

###########################################################
    def move_tel_raw(self,data):
        print 'Vamos a Mover telescopio a',data
        print data
        mando=data+' ACT'
        data, status = self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1
###########################################################
    def move_tel_shell(self,data):
        print 'Vamos a Mover telescopio a',data
        print data
        mando=data+' \n'
        data, status = self.manda(mando)
        if not status:
            print "bad"
            print data
            return -1
###########################################################
###########################################################
    def espera_telescopio_estable(self,pasos=5):
        print 'Esperando a que se estabilise el telescopio con tracking enable'
        espera=True
        if espera:
            self.lee_coordenadas()
            olddec=self.dec_sec
            oldar=self.ar_sec
            loop=True
            conta=0
            while loop:
                time.sleep(0.5)
                self.lee_coordenadas()
                print 'telescopio dec,ar',self.dec_dec,self.ar_dec
                d=self.esta_dentro_error(self.dec_sec,olddec,2.5)
                aa=self.esta_dentro_error(self.ar_sec,oldar,20)
                print d,aa,conta
                if (d) and aa:
                    conta+=1
                else: conta=0
                if conta >pasos: loop=False
                    
                olddec=self.dec_sec
                oldar=self.ar_sec
        
###########################################################
    def esta_dentro_error(self,data,deseado,error):
        #en segundos ahora
        #regresa booleano
        #error en porcentaje
        
        dmax=deseado+abs(error)
        dmin=deseado-abs(error)
        
        print 'dato=%3.3f, deseado=%3.3f, min=%3.3f, max=%3.3f '%(data,deseado,dmin,dmax)
        if data<dmax and data>dmin :return True
        else: return False
###########################################################
    def define_nuevas_coordenadas(self):
            #print 40*'^'
            print 'Definiendo nuevas coordenadas'
            
            data, status = self.manda('CORR \n')
            if not status:
                print "bad new cenit"
                print data
            time.sleep(2)
            
###########################################################
'''
a=TELESCOPIO84()
#a.lee_coordenadas()
#a.info()
a.espera_telescopio_estable()

'''
