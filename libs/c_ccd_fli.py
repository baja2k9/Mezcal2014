#!/usr/bin/env python

import time
#import socket
import gobject
import string

import c_ccd
from c_ccd import *
from c_cliente import *

import os
import c_ds9
import c_util
import c_analisis
import gtk

#V1.1 Dic-2010, pruebas en spm ->E.Colorado
#V1.2 Dic-2011, nuevo driver V1.99, cambios de lectura ->E.Colorado
#V1.3, pinta fail si no encuentra CCD
#V1.4 Jun-2011, cambios extras, roi-pol, dark subs, estadistica disable, etc
#V1.5 Jul-2012, se arreglo bug de roi cuando binning no era 1
#-----------------------------------------------------
class CCD_FLI(CCD,CLIENTE):
    __mytimeout = 10

    def __init__(self):
        self.tam_binario=0
        CCD.__init__(self)
        self.analisis=c_analisis.ANALISIS()
        #self.xsize_total=2080
        #self.ysize_total=2112
        self.xsize_total=2048
        self.ysize_total=2048

        self.xsize=2048
        self.ysize=2048
        self.gain=1

        self.xend=self.xsize
        self.yend=self.ysize

        self.xorg_ini=self.xorg=0
        self.yorg_ini=self.yorg=0
        self.tipo="Fli"
        self.label="fli CCD3041B1-V"
        self.label2="fli ProLine PL3041 (CCD3041)"
        self.usuario="fli ccd class"
        # valores default
        self.ip, self.puerto = "192.168.0.41", 9710
        #pruebas ensenada
        #self.ip, self.puerto = "localhost", 9710

        #control de temperaturas
        self.temp=-30.0
        self.temp_hilimit=-28.0
        self.temp_lowlimit=-25.0
        self.can_readtemp=True
        self.temp_base=0.0
        self.power=0.0
        #etiqueta gui ccd temp & power
        self.bpower="0.0 (0%)"

        #salidas
        self.output=1    #Num canales de salida actual
        self.default_output=1    #salida default
        self.output_anterior=1
        self.output_actual=1
        self.n_output=2    #Num canales de salida

        self.lista_speed=[
            ["2 Mhz @ 2 Chan",0],
            ["2 Mhz @ 1 Chan",1],
            ["500 Khz @ 1 Chan",2]]
        self.do_estadistica=False
        self.do_dark_subs=False
        #self.post_mando='./procesa'
        self.post_mando='dark'
        self.full_post_mando='/home/observa/David/dark'
        self.cmd_path='/home/observa/David/'
        self.ds9=c_ds9.DS9()
        #self.fli_file='/tmp/salida.fits'
        self.fli_file='salida.fits'
        self.util=c_util.UTIL()
        self.rotate_axis=False
        self.arscale=-0.265
        self.decscale=0.265
        self.extra_header=True
        self.data_cols=2048

############################################################################
    def __del__(self):
        print "cerrando driver de FLI"
        #self.set_temp(15)

        self.manda("SALIR ")
        self.manda("SALIR ")
############################################################################
    def full_frame(self):
        self.xorg=self.xorg_ini
        self.yorg=self.yorg_ini
        self.xsize=2048
        self.ysize=2048
        self.update()
############################################################################
    def update(self):
        x=self.xsize
        y=self.ysize
        self.xsize=x/self.cbin
        self.ysize=y/self.rbin
############################################################################
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
        #self.mis_variables.mensajes("CCD Temp="+str(self.temp))
        #todo de una vez
        self.get_temp_base()
        self.get_power()
        #construir etiqueta pal gui
        self.bpower="%3.2f (%3.2f %%)"%(self.temp_base,self.power)

        #mandar al gui
        self.mis_variables.msg_gui("FLI_BPOWER "+self.bpower)
        a="CCD Temp="+str(self.temp)+" CCD Temp_Base="+str(self.temp_base)+" CCD cooler Power="+str(self.power)

        self.mis_variables.mensajes(a)
############################################################################
    def get_temp_base(self):
        #print "leer la temperatura"
        t,s=self.manda("LEE_TEMP_BASE ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        t=t.split()
        self.temp_base=float(t[1])
        #self.mis_variables.mensajes("CCD Temp_Base="+str(self.temp_base))
############################################################################
    def get_power(self):
        t,s=self.manda("LEE_POWER ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        t=t.split()
        self.power=float(t[1])
        #self.mis_variables.mensajes("CCD cooler Power="+str(self.power))
############################################################################3
    def set_temp(self,temp):

        t,s=self.manda("SET_TEMP "+str(temp))
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1

############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT Fli Server (Finger Lake Instruments)")
        #data,status=self.manda_recibe("INIT ")
        #if not status:
        #    print "bad"
        #    print data
        #    self.mis_variables.mensajes(data,"Log")
        socket,status=self.manda_open("INIT ")
        if status:
            socket.setblocking(1)
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_fli(socket)
            socket.close()
            #poner canal default
            self.set_cam_mode(1)
            #self.set_temp(str(self.temp))
        else:
            self.stop=True
            self.mis_variables.mensajes(socket,"Log","rojo")
            print "No llego el mensaje de red"
############################################################################
    def lee_fli(self,socket):
        line=socket.makefile('r',1)	#manejo del socket tipo archivo
        while 1:
            data=line.readline().strip()
            if self.stop:   #verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
            try:
                txt=str(data)
                ok=True
            except:
                ok=False
            if ok:
                mando=txt.split()

                if string.join(mando[0:3]) == "info Visible area:":
                    print "info --",mando
                    x = mando[3].split(",")
                    print x
                    y = mando[4]
                    print y
                elif mando[0]=="info":
                    #self.mis_variables.mensajes(mando,"Log")
                    self.mis_variables.mensajes(txt)
                    print "info --",mando
                elif mando[0]=="GOOD":
                    self.mis_variables.mensajes(txt,"None","verde")
                elif mando[0]=="FAIL":
                    self.mis_variables.mensajes("FAIL, CCD Camera Not Found!","Log","rojo")
                elif mando[0]=="FAILFILTER":
                    self.mis_variables.mensajes("FAIL, Camera Filter Wheel Not Found!","Log","rojo")
                if mando[0]=="LEE_TEMP":
                    #print "llego temp"
                    self.mis_variables.update_temp(float(mando[1]))
                    self.mis_variables.mensajes(data)
            if not data:
                print "no mas datos"
                break
            if data=="CLOSE":
                print "llego close"
                break
        line.close()
        print "cerre socket init fli"
############################################################################
    def trae_binario(self):
        bin=self.tam_binario
        #print "En trae binario de FLI a sacar solo lo binario, bytes=%d",bin
        self.mis_variables.mensajes("MANDABIN Receiving %d Bytes"%(bin))

        if self.tam_binario != None and self.tam_binario > 0:
            socket,status=self.manda_open("MANDABIN ")
            if status != False:
                self.bindata = ''
                while len(self.bindata) < bin:
                    if self.stop:	#verifica si se presiono Cancelar
                        print "Trae_binario Cancelado"
                        break
                    temp = socket.recv(bin-len(self.bindata))
                    if temp == '':
                        break
                    self.bindata += temp
                    if len(self.bindata) >= bin:
                        break
                '''
                if self.stop == False:					#verifica si se presiono Cancelar
                    binario = open('imagen123.bin', 'wb')
                    binario.write(self.bindata)
                    binario.close()
                '''
            else:
                print "error----------"
                self.mis_variables.mensajes(socket,None,"rojo")
            socket.close()
        else:
            print "[Rx] BIN_SIZE ",bin
        self.stop=False
        print "Termine Mandabin FLI ---------------------------------------"
############################################################################
    def expone(self):
        print "exponinendo para FLI CAM ..................... "
        self.ccd_ready=False
        milisec=int(self.etime*1000)
        ccdmensaje="EXPONE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d "\
            %(milisec,\
            self.xsize, self.ysize,\
            self.cbin,self.rbin,\
            self.xorg*self.cbin,self.yorg*self.rbin,\
            not self.shutter)
        print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje)
        self.mis_variables.logging_debug(ccdmensaje)

        socket,status=self.manda_open(ccdmensaje)
        if status and self.stop==False:
            socket.setblocking(1)
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_MarconiServer(socket)
            socket.close()
        else:
            self.stop=True
            self.mis_variables.mensajes(socket,"Log","rojo")
            print "No llego el mensaje de red"
        self.mis_variables.update_barra("done.",0.001)

############################################################################
    def lee_ccd(self,socket):
        line=socket.makefile('r',1)
        while True:
            data = line.readline().strip()
            if self.stop:					#verifica si se presiono Cancelar
                print "Trae_binario Cancelado---------------------------------------------------------"
                break
            print data
            print time.time()
            if str(data) != "TERMINE" and str(data) != "CLOSE":
                tmp = self.procesa(data)
                if tmp != None:
                    self.tam_binario = tmp
                    print "------------------binario------------ %f"%self.tam_binario
            elif str(data) == "CLOSE":
                break
        line.close()
############################################################################
    def espera_estatus(self,t):
        print "Esperando FLI Cam.............................."
        while self.tam_binario==0 and self.stop==False:
            #print ".",
            #time.sleep(0.3)
            while gtk.events_pending():
                gtk.main_iteration()
            if self.stop:					#verifica si se presiono Cancelar
                print "Trae_binario Cancelado"
                break
        #time.sleep(2)
        time.sleep(0.5)
        print "FLI Cam Ready.............................."
############################################################################
    def set_cam_mode(self,modo=0):
        #cambio de canal y velocidad
        t,s=self.manda("SET_CAM_MODE "+str(modo))
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        #variables para el header
        self.output_anterior=self.output_actual
        self.output_actual=modo

############################################################################
    def cancela(self):
        print "Cancelando CCD FLI"
        data,s=self.manda("CANCELA ")
        if not s:
            print "bad"
            self.mis_variables.mensajes(data,"Log","rojo")
        print "Si mande cancela al CCD ",data

############################################################################
    def local_header(self,hdr=None):

        #print "Local header de FLI"

        hdr.set("TEMPBASE",float(self.temp_base), "FLI BASE CCD Temperature (celsius degree)",after="CCDTEMP")
        hdr.set("POWER",float(self.power), "FLI Peltier Cooler Power %",after="TEMPBASE")
        hdr.add_comment("Extra Header parameter for FLI Cameras only",after="CCDTEMP")

        #modificar
        #sera dual?
        if self.output_actual==0:
            used=2
        else:
            used=1

        hdr.set("NAMPS",2, 'Number of Amplifiers')
        hdr.set("CCDNAMPS",used, 'Number of amplifiers used')
        hdr.set("AMPNAME",self.lista_speed[self.output_actual][0], 'Amplifier name')
############################################################################
    def pre_expone(self):
        #para actualizar en el header CCD temp, base y power
        self.get_temp()
############################################################################
    def post_expone_old(self,archivo=None):
        #print "Pre-procesamiento de FLI --------------------------"

        if self.do_estadistica: s=1
        else: s=0

        if self.do_dark_subs: d=1
        else: d=0

        if self.do_estadistica or self.do_dark_subs:
            print "Si ha que procesar image de FLI",archivo
            mando="%s %s %d %d"%(self.post_mando,archivo,s,d)
            print mando
            a=self.util.ejecuta(mando)
            print 'a=',a
            self.mis_variables.mensajes(str(a),Color="azul")

            #Cargar la imagen procesada al ds9
            self.ds9.loadfile(self.fli_file)
            #a='xpaset -title MarconiOnly -scale Zscale -zoom to fit -orient y -rotate 90'
            #os.system(a)
############################################################################
    def post_expone(self,archivo=None):
        #print "Pre-procesamiento de FLI --------------------------"

        if self.do_estadistica: s=1
        else: s=0

        if self.do_dark_subs: d=1
        else: d=0

        if self.do_estadistica or self.do_dark_subs:
            print "Si ha que procesar image de FLI, pero despues",archivo




############################################################################
    def setup_first_image(self):
        self.mis_variables.mensajes("Setting DS9 defaults for FLI",Color="verde")
        self.ds9.set_mando(" scale zcale")
        self.ds9.set_mando(" zoom to fit")
        self.ds9.set_mando(" orient y")
        self.ds9.set_mando(" rotate 90")
############################################################################
    def apaga_sheeva(self):
        print "Haciendo shutdown a la PC SheevaPlug"
        C=CLIENTE()
        C.ip=self.ip
        C.puerto =4953
        C.manda_sin_respuesta("APAGAME Now")
############################################################################
    def __del__(self):
        print "********************* Destroy fli c_ccd CLASS ***********************************"
        CCD.__del__(self)
############################################################################
    def post_procesa_imagen(self,archivo=None,filtro=None):
        print 'fli post procesa',archivo,filtro
        print "binning",self.cbin,self.rbin,self.bin
        
        a1=self.cbin==1 and self.rbin==1
        a2=self.cbin==2 and self.rbin==2
        print a1,a2
        
        f=filtro=="U" or filtro=="B" or filtro=="V" or filtro=="R" or filtro=="I"
        if  a2 and f:
            print 'si vamos a procesar FLI con Flats'
            i=self.analisis.load_fit(archivo)
            ar="%s/flats_pola2/flat%d%s.fits"%(self.cmd_path,self.cbin,filtro)
            print 'flat',ar
            flat=self.analisis.load_fit(ar)
            print 'flat cargado'
            #generar dark
            mando="cd %s; %s/%s %f %d"%(self.cmd_path,self.cmd_path,self.post_mando,self.etime,self.cbin)
            print mando
            a=self.util.ejecuta(mando)
            print 'a=',a
            #cargar dark
            salida="%s/salida.fits"%self.cmd_path
            print 'vamos a carga dark',salida
            dark=self.analisis.load_fit(salida)
            print 'dark cargado'
            #resultado=(i-dark*0.9)/flat
            resultado=(i-dark*0.9)
            try:
                os.system("rm /tmp/salida2.fits")
            except:
                print 'No oude borrar /tmp/salida2.fits'
            print 'vamos a grabar resultado /tmp/salida2.fits'
            self.analisis.save_fit('/tmp/salida2.fits',resultado)
            #Cargar la imagen procesada al ds9v
            self.ds9.loadfile('/tmp/salida2.fits')
            
        if  a1 and f:
            print 'si vamos a procesar FLI sin Flats'
            i=self.analisis.load_fit(archivo)
            
            #ar="%s/flats_pola2/flat%d%s.fits"%(self.cmd_path,self.cbin,filtro)
            #print 'flat',ar
            #flat=self.analisis.load_fit(ar)
            #print 'flat cargado'
            #generar dark
            mando="cd %s; %s/%s %f %d"%(self.cmd_path,self.cmd_path,self.post_mando,self.etime,self.cbin)
            print mando
            a=self.util.ejecuta(mando)
            print 'a=',a
            #cargar dark
            salida="%s/salida.fits"%self.cmd_path
            print 'vamos a carga dark',salida
            dark=self.analisis.load_fit(salida)
            print 'dark cargado'
            resultado=(i-dark)
            try:
                os.system("rm /tmp/salida2.fits")
            except:
                print 'No pude borrar /tmp/salida2.fits'
            print 'vamos a grabar resultado /tmp/salida2.fits'
            self.analisis.save_fit('/tmp/salida2.fits',resultado)
            #Cargar la imagen procesada al ds9v
            self.ds9.loadfile('/tmp/salida2.fits')


############################################################################
