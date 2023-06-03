#!/usr/bin/env python


# -*- coding: utf-8 -*-
import time
from c_cliente import *

import c_ccd
from c_ccd import *
import os
import gtk

#V1.0, E.Colorado inicial
#usa al servidor alta_server en c++
#V2.0 Modificada para que sea compatible con la programa oan_ccds.py
############################################################################
class SBIG2(CLIENTE,CCD):
    'Clase para uso del cliente Andor Apogee '
    xsize_total=512
    ysize_total=512
    xsize=xsize_total
    ysize=ysize_total
    xend=xsize_total
    yend=ysize_total
    xorg=0
    yorg=0
    shutter=1
    temp=0
    bin=1
    model='unknown'
    dark=False
    etime=0.1
    outfile='/imagenes/image.fits'



############################################################################
    def __init__(self):
        CCD.__init__(self)
        self.datatype='fits'
        self.ip="localhost"
        #self.ip="192.168.0.127" #electronica ENS
        self.puerto=9765
        self.usuario="Apogee"	#para el debug de la clase cliente
         #V2
        self.tipo="Andor"
        self.label="Andor Apogee all"
        self.label2="Alta F260"
        self.xsize_total=512
        self.ysize_total=512
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        #no verificadas
        self.arscale=0.1423
        self.decscale=0.1423
        self.can_readtemp=True
        self.usuario="Apogee ccd class"

        self.gain=1

        self.output=0    #Num canales de salida actual
        self.default_output=0    #Num canales de salida
        self.n_output=1    #Num canales de salida
        self.default_output=1    #salida default
        self.output_actual=self.default_output


        #control de temperaturas
        self.temp=-20.0
        self.temp_hilimit=-25.9
        self.temp_lowlimit=-15.0
        self.can_readtemp=True

        self.use_trackccd=False
        self.power=0.0
        #etiqueta
        self.bpower="0%"

         #tracking CCD/home/observa
        self.txsize=self.txsize_total=0
        self.tysize=self.tysize_total=0
        self.Activeccd=0
        self.extra_header=True
############################################################################
    def inicializa(self):
        print "inicializando Apogee"
        socket,status=self.manda_open("INIT ")
        if status:
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_respuestas(socket)
            socket.close()
            self.set_temp(str(self.temp))
            self.get_ccdinfo()
        else:
            print "No llego el mensaje de red"
############################################################################
    def expone(self):
        self.ccd_ready=False
        print "exponinendo para apogee.......... "


        milisec = int(self.etime * 1000)
        ccdmensaje = "EXPONE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d " \
                     % (milisec, \
                        self.xsize, self.ysize, \
                        self.cbin, self.rbin, \
                        self.xorg * self.cbin, self.yorg * self.rbin, \
                        not self.shutter)

        print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje)

        socket,status=self.manda_open(ccdmensaje)
        #bloquear sockect para evitar timeout
        socket.setblocking(1)
        if status:
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_respuestas(socket)
            socket.close()
        else:
            print "No llego el mensaje de red"

############################################################################
    def get_temp(self):
        print "get_temp"
        data,status=self.manda("LEE_TEMP ")
        if not status:
            print "bad"
            print data
        #procesar respuesta
        #'Temp_sbig -4.82 C\nNet Ok\n'
        self.mis_variables.mensajes(data)
        mando=data.split()
        self.temp=float(mando[1])


        return self.temp
############################################################################
    def set_temp(self,temp):
        print "set_temp to ",temp
        data,status=self.manda("set_temp "+str(temp))
        if not status:
            print "bad"
            print data

############################################################################3
    def info(self):
        print "ANDOR model: ", self.model
        print "Dimensiones:", self.xsize_total," x ",self.ysize_total
        print "Origen:", self.xorg," x ",self.yorg
        print "Ventana:", self.xsize," x ",self.ysize
        print "Binning:", self.bin
        print "Shutter:", self.shutter
        print "Dark Substrac:", self.dark
        print "Exposure Time (s):",self.etime
        print "servidor Ip:",self.ip
        print "servidor Puerto",self.puerto
        print "Peltier Power",self.power
        print "Tracking CCD size:", self.txsize_total," x ",self.tysize_total
        print "Active CCD:",self.Activeccd
############################################################################
    def lee_respuestas(self,socket):
        line=socket.makefile('r',1)	#manejo del socket tipo archivo
        while 1:
            data=line.readline().strip()
            try:
                txt=str(data)
                ok=True
		print "--->",txt
            except:
                ok=False
            if ok:
                print "rx=",data
		self.mis_variables.mensajes(data)
		self.procesa_datos(data,socket)
            if not data:
                print "no mas datos...."
                break
            if data=="CLOSE" or data=="Net Ok":
                print "llego close"
                break

        print "lei todo red, termine !!!!!!!!!!!!!!!!!!!!!"
		#cerrar todo
        line.close()
        #socket.close()
############################################################################
    def procesa_datos(self,data,socket):

        binario=False
        mando=data.split()
        key=mando[0]
        #print "mando=",mando

        if key=="SBIGDISPLAY":
            print "llego SBIGDISPLAY"
            self.temp=float(mando[1])
            print "temp=",self.temp
            self.ccd_ready=True
            self.mis_variables.update_temp(self.temp)

        elif key=="Camera":
            #self.mis_variables.mensajes(data)
            self.model=mando[2]



############################################################################3
    def trae_binario(self):
        if self.ip=='localhost':
            print "los datos ya estan y son fits para la sbig ->/imagenes/image.fits"
        else:
            self.trae_fit()

############################################################################3
    def espera_estatus(self,t):
        print "esperando ccd ",self.label2," ",t,"s.........."
        while not self.ccd_ready:
            print '.',
            #self.mis_variables.gui_update()
	    while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.1)
            if self.stop:           #verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
        print "llego ccd ready !!!!!!!!!!!!",self.ccd_ready
############################################################################
    def get_power(self):
        print 'Get power'
        data,status=self.manda("get_power ")
        if not status:
            print "bad"
            print data
        #procesar respuesta
        #'Temp_sbig -4.82 C\nNet Ok\n'
        print 'power',data
        self.mis_variables.mensajes(data)
        mando=data.split()
        self.power=float(mando[3])
############################################################################
    def get_ccdinfo(self):
        print 'Get CCD Info'
        data,status=self.manda("get_ccdinfo ")
        if not status:
            print "bad"
            print data
        #procesar respuesta
        #'Temp_sbig -4.82 C\nNet Ok\n'
        self.mis_variables.mensajes(data)
        mando=data.split()

        #main CCD
        self.xsize=self.xsize_total=self.mxsize_total=int(mando[1])
        self.ysize=self.ysize_total=self.mysize_total=int(mando[2])

        #tracking CCD
        self.txsize=self.txsize_total=int(mando[3])
        self.tysize=self.tysize_total=int(mando[4])



############################################################################
    def get_activeccd(self):
        print 'Get active ccd'
        data,status=self.manda("get_activeccd ")
        if not status:
            print "bad"
            print data
        #procesar respuesta
        #'Temp_sbig -4.82 C\nNet Ok\n'
        self.mis_variables.mensajes(data)
        mando=data.split()
        self.Activeccd=int(mando[1])

############################################################################
    def set_activeccd(self,cual=0):
        print 'Set active CCD',cual
        data,status=self.manda("set_activeccd "+str(cual))
        if not status:
            print "bad"
            print data
        #procesar respuesta
        #'Temp_sbig -4.82 C\nNet Ok\n'
        self.mis_variables.mensajes(data)
        #mando=data.split()
        #self.power=int(mando[1])

        self.cambia_dimensiones(cual)
        self.Activeccd=cual

############################################################################
    def cambia_dimensiones(self,cual=0):
        if cual==0:
            print "Estamos usando CCD Principal:"
            self.xsize=self.xsize_total=self.mxsize_total
            self.ysize=self.ysize_total=self.mysize_total
        else:
            print "Estamos usando CCD de Tracking:"
            self.xsize_total=self.txsize=self.txsize_total
            self.ysize_total=self.tysize=self.tysize_total

############################################################################
    def pre_expone(self):
        #para actualizar en el header CCD temp, base y power
        self.get_temp()
############################################################################
    def local_header(self,hdr=None):

        print "Local header de APOGEE"


############################################################################
    def trae_fit(self):
        print 'En trae Fit'
        #forma rapida
        '''
        data,status=self.manda_recibe_archivo("manda_fit ",'a.fit')
        if not status:
            print "bad"
            print data
        '''
        mando='echo "manda_fit "|hose %s 9765 --slave >/imagenes/image.fits' %self.ip
        print mando
        os.system(mando)
        print 'End, trae_fit'


############################################################################
    #destrucctor
    def __del__(self):
        print "destructor de Apogee"
        self.manda("salir ")
############################################################################

