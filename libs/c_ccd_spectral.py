#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd
from c_ccd import *
from c_cliente import *
#import array
import gtk



class CCD_SPECTRAL(CCD, CLIENTE):

    'Clase para uso del CCD 4240 con electronica de Spectral instruments '

    def __init__(self):
        CCD.__init__(self)
        self.tipo = "SPECTRAL"
        self.label = "E2V (2k x 2k) Spectral"
        self.label2 = "E2V-4240"
        self.xsize_total = 2072
        self.ysize_total = 2048
        self.xsize = self.xsize_total
        self.ysize = self.ysize_total
        self.xend = self.xsize_total
        self.yend = self.ysize_total
        self.arscale = 0.2341
        self.decscale = 0.2341
        self.rotate_axis = False

        self.usuario = "Spectral ccd class"
        self.ip = "192.168.0.18"
        #self.ip = "red0"

        self.puerto = 9710
        #self.set_timeout(2)

        self.gain = 1
        '''
        self.output = 2  # Num canales de salida
        self.n_output = 2  # Num canales de salida
        self.default_output = 2  # salida default, right
        self.output_actual = self.default_output
        '''
        self.output = 0  # Num canales de salida
        self.n_output = 1  # Num canales de salida
        self.default_output = 0  # salida default, right
        self.output_actual = self.default_output
        self.INIT_COMMAND = "INIT "
        self.INIT_MSG = "CCD INIT Series  1100, from Spectal Instruments"
        # control de temperaturas
        self.temp = -110.0
        self.temp_hilimit = -105
        self.temp_lowlimit = -99.0
        self.can_readtemp = True

        self.extra_header = False
        self.data_cols = 2048
        self.lista_data = [2048, 2048, 999, 649, 474]
        self.cooler_status="?"
        self.x_status="?"
        self.lista_mode=[
            ["752 khz @ Mode 0, Attn=Low",0],
            ["400 khz @ Mode 1, Attn=High",1],
            ["200 Khz @ Mode 3, Attn=High",2]]
        self.modo=2

#############################################################################

    # destrucctor
    def __del__(self):
        print "destructor de MarconiServer"
        self.manda("close ")
        self.manda("salir ")
        self.manda("SALIR ")

#############################################################################

    def get_temp(self):
        # print "leer la temperatura"
        t, s = self.manda("LEE_TEMP ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(t, "Log", "rojo")
            return -1
        t = t.split()
        self.temp = float(t[1])
        self.mis_variables.mensajes("CCD Temp=" + str(self.temp))
        self.mis_variables.update_temp(self.temp)
#############################################################################

    def get_cooler(self):

        t, s = self.manda("COOLER_STATUS ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(t, "Log", "rojo")
            return -1
        print t
        t=t.split()
        self.cooler_status = int(t[1])

        self.mis_variables.mensajes("Cooler Status=" + str(self.cooler_status))
        #self.mis_variables.update_temp(self.temp)
        return self.cooler_status
#############################################################################
    def cooler_on(self):

        t, s = self.manda_sin_respuesta("COOLER_ON ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data, "Log", "rojo")
            return -1

        self.mis_variables.mensajes("Cooler ON")
#############################################################################
    def cooler_off(self):

        t, s = self.manda_sin_respuesta("COOLER_OFF ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data, "Log", "rojo")
            return -1

        self.mis_variables.mensajes("Cooler OFF")

#############################################################################

    def get_xstatus(self):
        # print "leer la temperatura"
        t, s = self.manda_recibe("showinfo ")
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(data, "Log", "rojo")
            return -1
        self.x_status = self.all_data_cliente
        print self.x_status

        #self.mis_variables.mensajes("Xtended Status=\n" + self.x_status)
        return self.x_status
        #self.mis_variables.update_temp(self.temp)
############################################################################

    def inicializa(self):
        print "inicializando CCD", self.label
        self.mis_variables.mensajes("********** WAIT **********", "noLog", "rojo")
        self.mis_variables.mensajes("*** Downloading CCD Firmware ***", "noLog", "rojo")
        self.mis_variables.mensajes(self.INIT_MSG)
        data, status = self.manda_recibe(self.INIT_COMMAND)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data, "Log", "rojo")
            self.mis_variables.msg_gui(
                "SHOW_ERROR " + "Fatal Error No CCD Server Found " + data)
            return -1

        print self.all_data_cliente
        self.get_temp()
        self.mis_variables.mensajes("***  CCD Spectral is READY ***", "noLog", "verde")
        self.cooler_on()
        
        return self.all_data_cliente

############################################################################
    def expone(self):
        print "Exponiendo ", self.label
        self.ccd_ready = False
        milisec = int(self.etime * 1000)
        ccdmensaje = "EXPONE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d LOOP=%d "\
            % (milisec,
               self.xsize, self.ysize,
               self.cbin, self.rbin,
               self.xorg, self.yorg,
               not self.shutter,
               # self.n_frames)
               1)

        print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje, "Log")

        socket, status = self.manda_open(ccdmensaje)
        if status:
            # mando bien el mensaje
            # vamos a recibir datos
            self.lee_MarconiServer(socket)
            socket.close()
        else:
            self.mis_variables.mensajes(socket, "Log", "rojo")
            print "No llego el mensaje de red"
        #data,status=self.manda_recibe("LEE_TEMP ")
        # data,status=self.manda(ccdmensaje)
        print "Fin CCD expone"

        self.mis_variables.update_barra("done.", 0.001)
############################################################################

    def trae_binario(self):
        bin = self.tam_binario
        print "En trae binario a sacar solo lo binario, bytes=", bin
        self.mis_variables.mensajes("MANDABIN Receiving %d Bytes" % (bin))

        if self.tam_binario != None and self.tam_binario > 0:
            socket, status = self.manda_open("MANDABIN ")
            if status != False:
                self.bindata = ''
                inicio = time.clock()
                while len(self.bindata) < bin:
                    if self.stop:  # verifica si se presiono Cancelar
                        print "Trae_binario Cancelado"
                        break
                    temp = socket.recv(bin - len(self.bindata))
                    if temp == '':
                        break
                    self.bindata += temp
                    if len(self.bindata) >= bin:
                        break
                # tiempo
                final = time.clock()
                tiempo = final - inicio
                print "Tarde en traer imagen via red %f segundos" % tiempo
                if tiempo == 0:
                    tiempo = 0.01
                speed = bin / tiempo / 1024.0
                texto = "Network Speed %3.2f KBYTES x sec" % speed
                self.mis_variables.mensajes(texto)
                print "Recibi TOTAL bytes,", len(self.bindata)
                socket.close()

            else:
                print "error----------"
                self.mis_variables.mensajes(socket, None, "rojo")
        else:
            print "[Rx] BIN_SIZE ", bin
        self.stop = False

############################################################################
    def espera_estatus(self, t):
        print "esperando ccd ", self.label2, " ", t, "s.........."
        while not self.ccd_ready:
            print '.',
            # self.mis_variables.gui_update()
            while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.1)
            if self.stop:  # verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
        print "llego ccd ready !!!!!!!!!!!!", self.ccd_ready

        # Espera para no volver exponer si leer la imagen
        # time.sleep(1)
        # print "La espera del status del CCD termino..."
############################################################################
    def cambia_salida(self):
        print "cambiando salida a", self.output
        mando = None
        if self.output[0] == 'Left':
            mando = 'AMPLI_B '
        elif self.output[0] == 'Right':
            mando = 'AMPLI_A '
        elif self.output[0] == 'Left & Right':
            mando = 'AMPLI_AB '
        print "mando=", mando
        if mando:
            data, s = self.manda(mando)
            if not s:
                print "bad"
                print data
                self.mis_variables.mensajes(data, "Log", "rojo")

############################################################################
    def cancela(self):
        print "Cancelando CCD Esopo"
        data, s = self.manda("CANCELA ")
        if not s:
            print "bad"
            self.mis_variables.mensajes(data, "Log", "rojo")
        print "Si cancelamos CCD ", data
        return
############################################################################

    def set_cam_mode(self,modo):
        print 'En cambio de modo para CCD spectral ->',modo
        self.modo=modo


        if modo==0:
            cmd='CONFIG_MODE0 '
        elif modo==1:
            cmd='CONFIG_MODE1 '
        elif modo==2:
            cmd='CONFIG_MODE2 '
        else:
            print "Modo del CCD no definido"

        t, s = self.manda_recibe(cmd)
        if not s:
            print "bad"
            print t
            self.mis_variables.mensajes(t, "Log", "rojo")
            return -1

        self.mis_variables.mensajes(cmd)
        self.mis_variables.mensajes(t)

############################################################################
    def local_header(self,hdr=None):

        #hdr.update("CCDMODE",str(self.lista_mode[self.modo][0]), 'CCD Readout Mode')
        hdr.set("CCDMODE", str(self.lista_mode[self.modo][0]), 'CCD Readout Mode')

#############################################################################
    def update_extra_header(self):
        pass
