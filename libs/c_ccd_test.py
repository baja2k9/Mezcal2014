#!/usr/bin/env python

#import time
#import socket
import gtk
import gobject



import c_ccd
from c_ccd import *
from c_cliente import *
import c_ds9

class CCD_TEST(CCD,CLIENTE):
    __mytimeout = 10

    def __init__(self):
        print "CCD test __init__"
        self.tam_binario=0
        CCD.__init__(self)
        self.xsize_total=1024
        self.ysize_total=1024
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.tipo="test"
        self.label="test"
        self.label2="test"
        self.usuario="test ccd class"
        # valores default
        self.ip, self.puerto = "localhost", 9710

        self.gain=1
        self.output=2    #Num canales de salida
        self.default_output=2    #Num canales de salida

        #control de temperaturas
        self.temp=-110.0
        self.temp_hilimit=-105
        self.temp_lowlimit=-99.0
        self.can_readtemp=True

        self.extra_header=True
        self.data_cols=1020

        self.n_output=2    #Num canales de salida
        self.default_output=2    #salida default, right
        self.output_actual=self.default_output
        #self.ds9=c_ds9.DS9()
############################################################################
    def inicializa(self):
        print "Inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT Fake Test networked With OAN Electronics")
        data,status=self.manda("INIT_FAKE ")
        if not status:
            self.stop=True
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log")
############################################################################
    def trae_binario(self):
        bin=self.tam_binario
        print "en trae binario a sacar solo lo binario, bytes=%d",bin
        self.mis_variables.mensajes("MANDABIN Receiving %d Bytes"%(bin))

        if self.tam_binario != None and self.tam_binario > 0:
            socket,status=self.manda_open("MANDABIN_FAKE ")
            if status != False:
                self.bindata = ''
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
############################################################################
    def expone(self):
##        data,status=self.manda("INIT_FAKE ")
##        if not status:
##            print "bad"
##            print data
##            self.mis_variables.mensajes(data,"Log","rojo")
##        else:
        print "exponinendo para test............. "
        self.ccd_ready=False
        milisec=int(self.etime*1000)
        ccdmensaje="EXPONE_FAKE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d LOOP=%d "\
            %(milisec,\
            self.xsize, self.ysize,\
            self.cbin,self.rbin,\
            self.xorg,self.yorg,\
            not self.shutter,\
            #self.n_frames)
            1)
        #print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje)
        self.mis_variables.logging_debug(ccdmensaje)

        socket,status=self.manda_open(ccdmensaje)
        socket.setblocking(1)
        if status:
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_MarconiServer(socket)
        else:
            self.stop=True
            self.mis_variables.mensajes(socket,"Log","rojo")
            print "No llego el mensaje de red"
        self.mis_variables.update_barra("done.",0.001)
        socket.close()
        print "\a"
############################################################################
    def lee_ccd(self,socket):
        line=socket.makefile('r',1)
        while True:
            data = line.readline().strip()
            if self.stop:					#verifica si se presiono Cancelar
                print "Trae_binario Cancelado"
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
        while self.tam_binario==0 and self.stop==False:
            while gtk.events_pending():
                gtk.main_iteration()
            if self.stop:					#verifica si se presiono Cancelar
                print "Trae_binario Cancelado"
                break
############################################################################
    def setup_first_image(self):
        #self.mis_variables.mensajes("Setting DS9 defaults for Test",Color="verde")
        #self.ds9.set_mando(" scale zcale")
        #self.ds9.set_mando(" zoom to fit")
        #self.ds9.set_mando(" orient y")
        #self.ds9.set_mando(" rotate 90")
        pass
