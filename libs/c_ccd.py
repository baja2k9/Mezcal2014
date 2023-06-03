#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################

import c_variables
from c_variables import *

#import c_weather
from c_weather import *

import c_astro
from c_astro import *

import c_telescopio
from c_telescopio import *
import c_telescopio_15
import c_telescopio_84
import c_telescopio_2m
#import c_telescopio_1m

#from c_telescopio_15 import *
#from c_telescopio_84 import *
#from c_telescopio_2m import *

import c_filtros
from c_filtros import *

import c_secundario
from c_secundario import *
import c_secundario_84
import c_secundario_15

import c_secundario_vacio
from c_secundario_vacio import *

import c_filtros_mexman
import c_filtros_ruca
import c_filtros_polima
import c_filtros_sempol
import c_filtros_italiana
import c_filtros_sbig5
import c_filtros_sbig8
import c_filtros_sbig10
import c_filtros_polima2
import c_filtros_espectropol

import c_tel_temp
import c_tel_temp_84
import os
import SocketServer
#import threading
#import thread

# V1.0 Inicio, E. Colorado
# V1.1 Anexe pre_expone y local header para poner cosas el clase
#      de los CCD's -->  E.Colorado Feb-2011
###########################################################################
class CCD(WEATHER,ASTRO):

    mis_variables = c_variables.VARIABLES()
    mi_filtro = c_filtros.FILTROS()
    mi_secundario = c_secundario.SECUNDARIO(mis_variables)
    mi_telescopio = c_telescopio.TELESCOPIO()
    mi_temp = c_tel_temp.TEL_TEMP()
    imgtype="image"
    DEBUG=False
###########################################################################
    def __init__(self):
        ASTRO.__init__(self)
        #print "Clase CCD BASE"
        self.bindata = ''
        self.datatype='raw'     #ara sabir si ya es fits o no
        self.stop=False
        self.tipo="TH7895"
        self.label="Photometrics CCD"
        self.label2="Star 1"
        self.xsize_total=512
        self.ysize_total=512
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.xorg=0
        self.yorg=0
        self.shutter=1
        self.temp=-120
        self.temp_hilimit=-110
        self.temp_lowlimit=-105
        self.noise=400
        self.cbin=1
        self.rbin=1
        self.bin=1
        self.gain=4
        self.speed=40e3
        self.full_image=1
        self.output=1    #Num canales de salida actual
        self.default_output=0    #salida default
        self.output_anterior=0
        self.output_actual=0
        self.n_output=1    #Num canales de salida

        self.n_frames=1    #frames
        self.etime=0.1    #segundos de exposicion
        self.can_readtemp=False
        self.can_readgain=False
        self.ts=''
        self.ut=''
        self.airmass = 1.00
        self.xtemp='-1 C'
        self.can_readprogress=False
        self.ccd_ready=False
        self.tam_binario=0
        self.readout_time=10
        self.pid = os.getpid()
        self.lista_output=[["1 Channel",0],["Left",1],["Right",2],["Left & Right",3]]
        self.mis_ccds = [["E2V (2k x 2k) Marconi5", "e2vm5"],
                         ["E2V Deep Depletion (2k x 2k) Marconi4", "e2vm4"], \
                         ["E2V Deep Depletion (2k x 2k) Marconi3", "e2vm3"], \
                         ["E2V (2k x 4k) Esopo", "e2ve"], \
                         ["E2V (2k x 4k) Esopo Rojo", "e2ver"], \
                         # ["E2V (2k x 2k) OAN","e2vo"],\
                         ["E2V (2k x 2k) Marconi2", "e2vm2"], \
                         ["Site 4", "SITE4"], \
                         ["Spectral Inst. (2k x 2k)", "SPECTRAL"], \
                         ["Spectral Inst. 2 (2k x 2k)", "SPECTRAL2"], \
                         ["Star 1 512 x 512", "TH7895"], \
                         ["Test Marconi Server", "test"], ["Finger Lakes Inst. (FLI)", "fli"], \
                         ["Sbig- All USB SBIG ", "sbig"], \
                         ["CCD Mil (Tona) 1024 x 1024", "TH7896"] \
                         ]

        #cuidar el orden
        self.lista_imagen=[["dark","d"],["flat","f"],["object","o"],["zero","b"],["arc","a"],["image",""],["movie",""]]
        self.ip="localhost"
        self.puerto=9999
        self.arscale=0.1423
        self.decscale=0.1423
        self.rotate_axis=True

        self.extra_header=False
        self.CCDSIZE='None'
        #self.CCDSUM=None
        #self.IMGSEC=None
        self.DATASEC='None'
        self.CCDSEC='None'
        self.BIASSEC='None'
        self.TRIMSEC='None'
        self.data_cols=1024 #total de datos buenos del ccd, en columnas
        self.is_first_image=True
        self.bin_n_roi=True	   #Se puede hacer ROI con Binning ??
        self.do_dark_subs=False

############################################################################
    def cambiaFiltro(self, filtro):
        print "Cambiando obj filtro a",filtro
        if filtro=="Ruca":
            print "Cambiando obj a Ruca"
            self.mi_filtro = c_filtros_ruca.RUCA(self.mis_variables)
        if filtro=="Mexman":
            print "Cambiando obj a Mexman"
            self.mi_filtro = c_filtros_mexman.MEXMAN(self.mis_variables)
        if filtro=="polarimetro":
            print "Cambiando obj a polarimetro"
            self.mi_filtro = c_filtros_polima.POLIMA(self.mis_variables)
        if filtro=="sempol":
            print "Cambiando obj a sempol"
            self.mi_filtro = c_filtros_sempol.SEMPOL(self.mis_variables)
        if filtro=="Italiana":
            print "Cambiando obj a Italiana"
            self.mi_filtro = c_filtros_italiana.ITALIANA(self.mis_variables)
        if filtro=="Sbig_5_Filters":
            print "Cambiando obj a Sbig_5_Filters"
            self.mi_filtro = c_filtros_sbig5.SBIG5W(self.mis_variables)
	if filtro=="Sbig_8_Filters":
            print "Cambiando obj a Sbig_8_Filters"
            self.mi_filtro = c_filtros_sbig8.SBIG8W(self.mis_variables)
        if filtro=="Sbig_10_Filters":
            print "Cambiando obj a Sbig_10_Filters"
            self.mi_filtro = c_filtros_sbig10.SBIG10W(self.mis_variables)
        if filtro=="Polima2":
            print "Cambiando obj a Polima2"
            self.mi_filtro = c_filtros_polima2.POLIMA2(self.mis_variables)
        if filtro == "EspectroPol":
            print "Cambiando obj a Espectropol"
            self.mi_filtro = c_filtros_espectropol.ESPECTROPOL(self.mis_variables)

############################################################################
    def cambia_telescopio(self, telescope):
        print "usando telescopio",telescope

        if telescope == "0.84m":
            self.mi_secundario = c_secundario_84.SEC84(self.mis_variables)
            self.mi_telescopio = c_telescopio_84.TELESCOPIO84(self.mis_variables)
            self.mi_temp=c_tel_temp_84.TEL_TEMP84()
        elif telescope == "1.5m":
            self.mi_secundario = c_secundario_15.SEC15(self.mis_variables)
            self.mi_telescopio = c_telescopio_15.TELESCOPIO15(self.mis_variables)
        elif telescope == "2.12m":
            self.mi_telescopio = c_telescopio_2m.TELESCOPIO2M(self.mis_variables)
	#elif telescope == "1m":
            #self.mi_telescopio = c_telescopio_1m.TELESCOPIO1M(self.mis_variables)
        else:
            print 'sin secundario'
            self.mi_secundario = c_secundario_vacio.SECVACIO(self.mis_variables)

############################################################################
    def cambia_escala_placa(self, telescope,ccd):
        print "fijando escala de placa para ",telescope, "con ccd",ccd,
		#OJO si se rota eje, los lo de dec sera AR
        if telescope == "0.84m":
            if ccd=="e2vm" or ccd=="e2vm2" or ccd=='e2ve':
                self.decscale=+0.2341
                #self.arscale =0.2396
                self.arscale =-0.2341
            elif ccd=='TH2K':
                self.decscale=0.266
                self.arscale =0.266
            elif ccd=='site5' or ccd=='site4':
                #0.390 de zurita
                self.decscale=-0.426
                self.arscale =0.426

        elif telescope == "1.5m":
            if ccd=="e2vm" or ccd=="e2vm2" or ccd=='e2ve':
                self.decscale=0.1423
                self.arscale =0.1423
            elif ccd=='TH2K':
                self.decscale=-0.158
                self.arscale =0.158
            elif ccd=='site5' or ccd=='site4':
                self.decscale=-0.253
                self.arscale =0.253

        elif telescope == "2.12m":
            if ccd=="e2vm" or ccd=="e2vm2" or ccd=='e2ve':
                self.decscale=0.2218*1.08
                self.arscale= 0.2218 *1.13
            elif ccd=='TH2K':
                self.decscale=-0.158
                self.arscale =0.158
            elif ccd=='site5' or ccd=='site4':
                self.decscale=0.426
                self.arscale =0.426

        print " escala dec ",self.decscale, "ar",self.arscale
############################################################################

    def ccd_info(self):
        print "----------------------------------------------------------------"
        print "CCD info: ", self.label,self.tipo,self.label2
        print "Dimensiones:", self.xsize_total," x ",self.ysize_total
        print "Origen:", self.xorg," x ",self.yorg
        print "Ventana:", self.xsize," x ",self.ysize
        print "Binning:", self.cbin," x ",self.rbin
        print "speed:", self.speed
        print "Gain:", self.gain
        print "Full image?:", self.full_image
        try:
            print "CCD output:",self.lista_output[self.output]
        except:
            print "CCD output:",self.output
        print "# Frames:",self.n_frames
        print "Exposure Time (s):",self.etime
        print "servidor Ip:",self.ip
        print "servidor Puerto",self.puerto
############################################################################
    def set_ip(self,ip):
        self.ip=ip
############################################################################
    def set_puerto(self,puerto):
        self.puerto=puerto
############################################################################
    def inicializa(self):
        pass
############################################################################
    def get_temp(self):
        print "Con este CCD no se lee la temperatura"
        return 100
############################################################################
    def pixeles(self):
        self.npixel=self.xsize*self.ysize
############################################################################
    def full_frame(self):
        self.xorg=self.yorg=0
        self.update()
############################################################################
    def update(self):
        self.xsize=self.xsize_total/self.cbin
        self.ysize=self.ysize_total/self.rbin
############################################################################
    def revisa_valores(self):
        #valor inicial no menor de 0
        if (self.xorg < 0):
            self.xorg=0

        if (self.yorg < 0):
            self.yorg=0

        #revisar origen en y no sea mayor al limite del ccd
        if (self.xorg >self.xsize_total):
            self.xorg=self.xsize_total-1

        if (self.yorg >self.ysize_total):
            self.yorg=self.ysize_total-1

        #revisar borde final
        if (self.xend > self.xsize_total or self.xend <1 ):
            self.xend=self.xsize_total

        if (self.yend > self.ysize_total or self.yend <1 ):
            self.yend=self.ysize_total

        if self.xorg+self.xsize > self.xsize_total:
            self.xsize = self.xsize - ((self.xorg + self.xsize) - self.xsize_total)
        if self.yorg+self.ysize > self.ysize_total:
            self.ysize = self.ysize - ((self.yorg + self.ysize) - self.ysize_total)

        #revisar tam. de ventana en x
        if (self.xsize>self.xsize_total or self.xsize<0):
            self.xsize=self.xsize_total
            print "aqui 1"

        if (self.ysize>self.ysize_total or self.ysize<0):
            self.ysize=self.ysize_total
            print "aqui 2"


        #verificar que las coordenadas sean pares
        if (self.xsize %2 !=0):
            #es impar
            self.xsize -=1

        if (self.ysize %2 !=0):
            self.ysize -=1

        if (self.xorg %2 !=0):
            self.xorg -=1

        if (self.yorg %2 !=0):
            self.yorg -=1
        #verificar si es roi
        x=self.xsize_total==(self.xsize-self.xorg )
        y=self.ysize_total==(self.ysize-self.yorg )
        z=x and y
        #print "x= ",x," y= ",y," z= ",z
        self.full_image=z
        self.pixeles()
###########################################################################
    def expone(self):
        print "exponinendo no esta implementada aqui"
###########################################################################
    def ciclo(self):
        while True:
            print "thread corriendo ",str(self.pid)
            time.sleep(3)
###########################################################################
    def salida (self):
        print "salida implementada en cada ccd"
###########################################################################
    def cancela(self):
        print "has el cancela un tu clase"
###########################################################################
    def cambia_salida(self):
        print "has el cambia salida un tu clase"
###########################################################################
    def lee_MarconiServer(self,socket):
        line=socket.makefile('r',1)	#manejo del socket tipo archivo
        binario = 0
        ok=True #todo bien
        while 1:
            data=line.readline().strip()
            if self.stop:					#verifica si se presiono Cancelar
                print "c_ccd ->Espera_estatus Cancelado"
                ok=False
                break
            try:
                txt=str(data)
                ok=True
            except:
                ok=False
            if ok:
                binario=self.procesa_datos_MarconiServer(data)
                if binario >0:
                    self.tam_binario=binario
            if not data:
                #print "no mas datos"
                break
            if data=="CLOSE":
                #print "llego close"
                break
        line.close()
        #print "lei todo red Esopo"
        #print "cerre socket esopo"
        return ok
############################################################################
    def procesa_datos_MarconiServer(self,data):
        #print "procesando datos de MarconiServer"
        if len(data)<1:
            print "No tengo datos del socket.."
            return False
        binario=0
        mando=data.split()
        key=mando[0]
        if key=="LEE_TEMP":
            #print "llego temp"
            self.mis_variables.update_temp(float(mando[1]))
	    self.temp=float(mando[1])
            self.mis_variables.mensajes(data)
        elif key=="READING":
            #print "Llego reading...", mando[1]
            t=key+" "+mando[1]+" %"
            #self.mis_variables.mensajes(t)
            #poner barra roja
            self.mis_variables.update_barraColor('red')
            self.mis_variables.update_barra(t,float(mando[1]))
        elif key=="BINARIO":
            #print "llego binario ", mando[1]
            #realmente manda pixeles
            binario=int(mando[1])
            binario*=2
            #self.ccd_ready=True
	elif key=="TERMINE":
	    print "Llego TERMINE, entonces hago CCD=READY"
	    self.ccd_ready=True
        elif key=="ESTADISTICA":
            #no es valida esta estadistica, es vieja
            self.mis_variables.mensajes(data)
        elif key=="TIME":
            #self.mis_variables.mensajes(data)
            t=key+" Progress "+mando[1]+" % (R="+mando[3]+" s)"
            #poner barra azul
            self.mis_variables.update_barraColor('blue')
            self.mis_variables.update_barra(t,float(mando[1]))
        elif key=="GOOD":
            self.mis_variables.mensajes(data,'Log','verde')
        elif key=="FAIL":
            self.mis_variables.mensajes(data,'Log','rojo')
        elif key == "TIME_REMAINING":
            tr = self.etime*1000 - int(mando[1])
	    if self.etime==0:
		ptr=100.0
	    else:
            	ptr = tr*100/(self.etime*1000)
            tr = tr/1000
            t="Progress %.2fs"% (tr)
            self.mis_variables.update_barraColor('blue')
            self.mis_variables.update_barra(t,ptr)
        return binario
############################################################################
    def espera_estatus(self,t):
        pass

############################################################################
    def update_extra_header(self):

        #print "*********************extra header*****************************************************"
        ###CCDSIZE
        '''
        The logical unbinned size of the CCD in section notation.  Normally
        this would be the physical size of the CCD unless drift scanning
        is done.  This is the full size even when subraster readouts are
        done.
        '''
        self.CCDSIZE="[1:%d,1:%d]"%(self.xsize_total,self.ysize_total)
        if self.DEBUG: print "CCDSIZE",self.CCDSIZE

        #self.CCDSUM=None

        #self.DATASEC="[1:%d,1:%d]"%(self.xsize,self.ysize)
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
        #print "CCDSEC",self.CCDSEC


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
            first_col= (self.data_cols-self.xorg)/self.cbin+1
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
        first_col=self.xorg
        ini=(self.xsize_total-self.data_cols)/self.cbin+1
        #tenemos overscan inicial en la imagen?
        if first_col <ini:
            #print "si hay overscan"
	    pass
        else:
            ini=1

        ##tenemos overscan final en la imagen?
        first_col=self.xorg+1
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            last_cols=self.xsize
        else:
            last_cols=self.data_cols/self.cbin

        self.CCDSEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        self.TRIMSEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        if self.DEBUG: print "TRIMSEC",self.TRIMSEC
############################################################################
    def local_header(self,hdr=None):
        pass
############################################################################
    def pre_expone(self):
        pass
############################################################################
    def post_expone(self,archivo=None):
        pass
############################################################################
    def setup_first_image(self):
        pass
############################################################################
    def __del__(self):
	print "********************* Destroy c_ccd CLASS ***********************************"
	#para que corra destructor
	try:
	    del self.mi_filtro
	except:
	    print "algo paso, no pude borrar clase mi_filtro"
