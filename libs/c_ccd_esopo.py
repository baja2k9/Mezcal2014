#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd
from c_ccd import *
from c_cliente import *
import gtk

#import array

#2010, eco, funciona solo con servidor nuevo, marconiServer
class CCD_ESOPO(CCD,CLIENTE):
    'Clase para uso del CCD Esopo con electronica de Astronomical Research Camera '
    def __init__(self):
		CCD.__init__(self)
		print "ESOPO 2014"
		self.tipo="e2ve"
		self.label="E2V (2k x 4k) Esopo"
		self.label2="E2V-4290"
		self.xsize_total=2048
		self.ysize_total=4612
		self.xsize=self.xsize_total
		self.ysize=self.ysize_total
		self.xend=self.xsize_total
		self.yend=self.ysize_total
		
		#escalas se usan en c_ccd cambia_escala
		self.arscale=0
		self.decscale=0
		#ojo al rotar eje
		self.rotate_axis=True
		

		self.usuario="Esopo ccd class"
		self.ip="192.168.0.40"

		self.puerto=9710
		self.gain=1

		self.output=2    #Num canales de salida
		self.n_output=2    #Num canales de salida
		self.default_output=2    #salida default, right
		self.output_actual=self.default_output

		self.INIT_COMMAND="INIT_4290 "
		self.INIT_MSG="CCD INIT_4290 Esopo Blue from Astronomical Research Cameras"
		#control de temperaturas
		self.temp=-110.0
		self.temp_hilimit=-105
		self.temp_lowlimit=-99.0
		self.can_readtemp=True

		self.extra_header=True
		self.data_cols=2048
		self.lista_data=[2048,2048,999,649,474]

############################################################################3
    #destrucctor
    def __del__(self):
		print "destructor de MarconiServer"
		self.manda("close ")
		self.manda("salir ")
		self.manda("SALIR ")

############################################################################3
    def get_temp(self):
        #print "leer la temperatura"
        t,s=self.manda("LEE_TEMP ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(t,"Log","rojo")
            return -1
        t=t.split()
        self.temp=float(t[1])
        self.mis_variables.mensajes("CCD Temp="+str(self.temp))
	self.mis_variables.update_temp(self.temp)
############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes(self.INIT_MSG)
        data,status=self.manda_open(self.INIT_COMMAND)
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
    def expone(self):
        print "exponinendo ",self.label
        self.ccd_ready=False
        milisec=int(self.etime*1000)
        ccdmensaje="EXPONE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d LOOP=%d "\
        %(milisec,\
        self.xsize, self.ysize,\
        self.cbin,self.rbin,\
        self.xorg,self.yorg,\
        not self.shutter,\
        #self.n_frames)
        1)

        #print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje,"Log")

        socket,status=self.manda_open(ccdmensaje)
        if status:
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_MarconiServer(socket)
	    socket.close()
        else:
            self.mis_variables.mensajes(socket,"Log","rojo")
            print "No llego el mensaje de red"
        #data,status=self.manda_recibe("LEE_TEMP ")
        #data,status=self.manda(ccdmensaje)
        print "Fin CCD expone"

        self.mis_variables.update_barra("done.",0.001)
############################################################################
    def trae_binario(self):
        bin=self.tam_binario
        print "En trae binario a sacar solo lo binario, bytes=",bin
        self.mis_variables.mensajes("MANDABIN Receiving %d Bytes"%(bin))

        if self.tam_binario != None and self.tam_binario > 0:
            socket,status=self.manda_open("MANDABIN ")
            if status != False:
                self.bindata = ''
                inicio= time.clock()
                while len(self.bindata) < bin:
                    if self.stop:					#verifica si se presiono Cancelar
                        print "Trae_binario Cancelado"
                        break
                    temp = socket.recv(bin-len(self.bindata))
                    if temp == '':
                        break
                    self.bindata += temp
                    if len(self.bindata) >= bin:
                        break
                #tiempo
                final= time.clock()
                tiempo= final-inicio
                print "Tarde en traer imagen via red %f segundos"%tiempo
                if tiempo==0: tiempo=0.01
                speed=bin/tiempo/1024.0
                texto="Network Speed %3.2f KBYTES x sec" %speed
                self.mis_variables.mensajes(texto)
                print "Recibi TOTAL bytes,",len(self.bindata)
		socket.close()

                '''
                if self.stop == False:					#verifica si se presiono Cancelar
                    binario = open('imagen123.bin', 'wb')
                    binario.write(self.bindata)
                    binario.close()
                '''
            else:
                print "error----------"
                self.mis_variables.mensajes(socket,None,"rojo")
        else:
            print "[Rx] BIN_SIZE ",bin
        self.stop=False

############################################################################
    def espera_estatus(self,t):
        print "esperando ccd ",self.label2," ",t,"s.........."
        while not self.ccd_ready:
            print '.',
            #self.mis_variables.gui_update()
	    while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.1)
            if self.stop:					#verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
        print "llego ccd ready !!!!!!!!!!!!",self.ccd_ready

	#Espera para no volver exponer si leer la imagen
        #time.sleep(1)
        #print "La espera del status del CCD termino..."
############################################################################
    def cambia_salida(self):
        print "cambiando salida a",self.output
        mando=None
        if self.output[0]=='Left':
            mando='AMPLI_L '
        elif self.output[0]=='Right':
            mando='AMPLI_R '
        elif self.output[0]=='Left & Right':
            mando='AMPLI_LR '
        print "mando=",mando
        if mando:
            data,s=self.manda(mando)
            if not s:
                print "bad"
                print data
                self.mis_variables.mensajes(data,"Log","rojo")

############################################################################
    def cancela(self):
        print "Cancelando CCD Esopo"
        data,s=self.manda("CANCELA ")
        if not s:
            print "bad"
            self.mis_variables.mensajes(data,"Log","rojo")
        print "Si cancelamos CCD ",data
        return
############################################################################
    def update_extra_header(self):

        print "extra header del Esopo"
        #considerad datos de overscan segun binning
        self.data_cols=self.lista_data[self.cbin]
        print "data cols",self.data_cols
        ###CCDSIZE
        '''
        The logical unbinned size of the CCD in section notation.  Normally
        this would be the physical size of the CCD unless drift scanning
        is done.  This is the full size even when subraster readouts are
        done.
        '''
        self.CCDSIZE="[1:%d,1:%d]"%(self.xsize_total,self.ysize_total)
        print "CCDSIZE",self.CCDSIZE


        ###DATASEC
        ini=1
        ##tenemos overscan final en la imagen?
        first_col=self.xorg+1
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            last_cols=self.xsize
        else:
            #last_cols=self.data_cols/self.cbin
            last_cols=self.data_cols-self.xorg
        self.DATASEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        print "DATASEC",self.DATASEC

        #self.DATASEC="[1:%d,1:%d]"%(self.xsize,self.ysize)
        #self.DATASEC="[%d:%d,%d:%d]"%(self.xorg+1,self.xsize,self.yorg+1,self.ysize)
        #print "DATASEC",self.DATASEC

        ###CCDSEC
        #es DATASEC sin binning
        '''
        The unbinned section of the logical CCD pixel raster covered by the
        amplifier readout in section notation.  The section must map directly
        to the specified data section through the binning and CCD to
        image coordiante transformation.  The image data section (DATASEC)
        is specified with the starting pixel less than the ending pixel.
        Thus the order of this section may be flipped depending on the
        coordinate transformation (which depends on how the CCD coordinate
        system is defined).
        '''
        #self.CCDSEC="[1:%d,1:%d]"%(self.xsize*self.cbin,self.ysize*self.rbin)
        self.CCDSEC="[%d:%d,%d:%d]"%(self.xorg*self.cbin+1,self.xsize*self.cbin,self.yorg*self.rbin+1,self.ysize*self.rbin)
        print "CCDSEC",self.CCDSEC


        ###BIASSEC
        '''
        Section of the recorded image containing overscan or prescan data.  This
        will be in binned pixels if binning is done.  Multiple regions may be
        recorded and specified, such as both prescan and overscan, but the
        first section given by this parameter is likely to be the one used
        during calibration.
        '''
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            #no hay overscan
            self.BIASSEC='None'
        else:
            #first_col= (self.data_cols-self.xorg)/self.cbin+1
            first_col= (self.data_cols-self.xorg)+1
            if first_col <1: first_col=1
            self.BIASSEC="[%d:%d,1:%d]"%(first_col,self.xsize,self.ysize)
        print "BIASSEC",self.BIASSEC

        ###TRIMSEC
        #datos del CCD sin overscan, o sea lo restante de BIASSEC
        '''
        Section of the recorded image to be kept after calibration processing.
        This is generally the part of the data section containing useful
        data.  The section is in in binned pixels if binning is done.
        '''
        """
        first_col=self.xorg
        ini=(self.xsize_total-self.data_cols)/self.cbin+1
        #tenemos overscan inicial en la imagen?
        if first_col <ini:
            print "si hay overscan"
        else:
            ini=1
        """
        ini=1
        ##tenemos overscan final en la imagen?
        first_col=self.xorg+1
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            last_cols=self.xsize
        else:
            #last_cols=self.data_cols/self.cbin
            last_cols=self.data_cols-self.xorg
        self.TRIMSEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        print "TRIMSEC",self.TRIMSEC
############################################################################
############################################################################
    def clear_ccd(self,cuantos):
        #print "leer la temperatura"
	a='CLEAR %d '%(cuantos)
        t,s=self.manda(a)
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1

#a=CCD_ESOPO()
#a.get_temp()

print "Class CCD ESOPO Ready.........."
