#!/usr/bin/env python

#V1.1 E. Colorado, Jun-2011 >Varios bug arreglados
#V1.2 E. Colorado, Nov-2011 -> Arregle formato DEC para header
#V1.3 E. Colorado, Ene-2012 -> Use zfil lpara  formato DEC
#V1.4 E. Colorado, May-2019 -> Modifique por nueva consola
#V1.5 E. Colorado, May-2019 -> Cambio de signo por mal offset en AR consola nueva

from  c_telescopio import *

###########################################################
class TELESCOPIO2M(TELESCOPIO):
    'Pide estado de los telescopios en SPM'

    def __init__(self,variables=None):
        self.mis_variables = variables
        self.usuario="Tel. 2.12m"
        self.ip = '192.168.0.208'
        self.puerto = 4955

        self.set_timeout(1)
        self.dec_pid = ''
        self.ar_pid = ''
        self.frenos = True
        self.limites = ''
        self.estado = '?'
        self.track_state = 'No Tracking'
        self.DEBUG = self.debug = False
        self.ar_dec = 0
        self.ar_old = 0
        self.dec_dec = 31
        self.dec_old = 31
        self.ah_dec = 0
        self.ah_old = 0
        self.on_zenith = True

        self.errors = 0

    ###########################################################
    def lee_coordenadas(self):

        rx = 0
        try:
            data, status = self.manda("TEL")
        except:
            return False

        if not status:
            #print "bad"
            self.errors += 1
            if self.errors < 5:
                print data
            #self.mis_variables.mensajes_obj(data, "Log", "rojo")
            return False
        self.errors=0
        # print "recibi",data
        rx = data
        # print "rx=", rx
        if rx == 0:
            print "error"
            return False

        data_ok = False
        datos = rx.split('\n')
        datos = ''.join(datos)
        #print 'llego de tel', datos

        # ['AhG  2.178686 DeCG 8.756805 AH +02:10:43.27 DEC +08:45:24.50 AR 19:50:55.97 CA_AHD 0.0 ESTADO_G 0  TS 22:01:39.24']OK

        i = datos.find('AR')
        if i:
            # sacar ar
            data_ok = True
            ar = datos[i + 2:]
            ar = ar.split()
            # print 'aqui',ar
            self.ar = ar[0]
            a = ar[0].split(':')
            #print 'ar', a

            self.gar = int(a[0])
            self.mar = int(a[1])
            self.sar = float(a[2])

            self.ar_sec = self.gar * 3600 * 15 + self.mar * 60 * 15 + self.sar * 15
            self.ar_dec = abs(self.gar) + abs(self.mar / 60.0) + abs(self.sar / 3600.0)
            # print 'ar dec',self.ar_dec
        else:
            data_ok = False
            return False

        i = datos.find('DEC')
        if i:
            dec = datos[i + 4:]
            # print 'dec', dec
            a = dec.split()
            self.dec = a[0]
            a = a[0].split(':')
            #print 'dec', a

            self.signo_dec = a[0][0]
            #print 'signo dec', self.signo_dec

            self.gdec = int(a[0])
            self.mdec = int(a[1])
            self.sdec = float(a[2])

            # self.dec=self.signo_dec+  str(self.gdec)+":"+str(self.mdec).zfill(2)+":"+str(self.sdec)
            # self.dec = str(self.gdec) + ":" + str(self.mdec).zfill(2) + ":" + str(self.sdec)

            if self.signo_dec == "-":
                signo = -1
            else:
                signo = 1
            self.dec_dec = (abs(self.gdec) + abs(self.mdec / 60.0) + abs(self.sdec / 3600.0)) * signo
            self.dec_sec = self.dec_dec * 3600

        # ah
        i = datos.find('AH')
        if i:
            ah = datos[i + 3:]
            a = ah.split()
            self.ah = a[0]
            a = a[0].split(':')
            #print 'ah', a

            self.signo_ah = a[0][0]
            #print 'signo ah', self.signo_ah

            self.hah = int(a[0])
            self.mah = int(a[1])
            self.sah = float(a[2])
            # print "My AH %d %d %2.1f" %  (self.hah , self.mah , self.sah)
            if self.signo_ah == "-":
                signo = -1
            else:
                signo = 1
            self.ah_dec = (abs(self.hah) + abs(self.mah / 60.0) + abs(self.sah / 3600.0)) * signo
            #print 'ah_dec', self.ah_dec

        #checar estado del tracking
        return True
    #######################################################
    def lee_coordenadas_una(self):
        #print self.edotel
        rx=0

        rx, s = self.manda("TEL")
        if not s:
            print "bad"
            print rx
            #self.mis_variables.mensajes(rx, "Log", "rojo")
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
        offset=-1*offset
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
