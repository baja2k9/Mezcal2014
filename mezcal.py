#!/usr/bin/env python
# -*- coding: utf-8 -*-
# V2.01 -E.Colorado, Version que deje en SPM el lluvioso 7 de Oct 2014, primera version de SPM
# V2.12 -E.Colorado,Mayo-2015, arregle bugcito que slits y filters
# V2.13 -E.Colorado,Ago-2015, puse decision para usar en mac en casa
# V2.14 -E.Colorado,Ago-2015, siempre despues de sequencia pongo obturador en remoto (control CCD)
# V2.15 -E.Colorado,Sep-2016, cambio de signo en escala de placa con cambio de canal de lectura left
# V2.20 -E.Colorado,Ago-2017, Hice cambio para que funcionara el roi 2 center con CCD Spectral2, arregle bug en pdf, bias en macro no era cero la ultima
# V2.22 -E.Colorado,Ago-2018, Bugs reportados por M. richer arreglados
# V2.23 -E.Colorado,Jun-2023, Bugs reportados por M. richer , compu nueva, gui delay se tardaba de mas

import pygtk
pygtk.require("2.0")
import gtk,gtk.glade
from gtk import gdk
import gobject
import sys
import time
import threading
import thread
import string
import os
import Queue
import math
from shutil import copy2

#from shutil import copy2

sys.path.append("/usr/local/instrumentacion/Mezcal2014/libs")
import mezcal_motores
from mezcal_motores import *
import c_ds9

import c_bin2fits
from c_bin2fits import *

#clases de los CCDs
import c_ccd_star1
import c_ccd_th2k
import c_ccd_test
try:
    import c_ccd_fli
except:
    print 'No pude cargar CCD FLI'
import c_ccd_marconi
import c_ccd_marconi2
import c_ccd_marconi3
import c_ccd_marconi4
import c_ccd_esopo
import c_ccd_site4
import c_ccd_site5
import c_ccd_sbig2
import c_ccd_mil
import c_ccd_spectral
import c_ccd_spectral_2
import c_util
import c_ambiente2

import c_backup_oan
from c_backup_oan import *

import c_mez_macros
import csv

import platform
print 'os',platform.system()

if platform.system()=='Linux':
    sys.path.append("/usr/local/instrumentacion/guiador2m_cliente")
else:
    sys.path.append("/Users/colorado/Progs/guiador2m_cliente") #mac

import guiador2m_cliente
from c_gplatina import *

gobject.threads_init()
###########################################################
class MEZCAL(object,MEZCAL_MOTORES,BIN2FITS,BACKUP,GPLATINA):
    'Manejo del instrumento Mezcal'

###########################################################
    def __init__(self):

        print "**** iniciando mezcal V2 ****"

        BIN2FITS.__init__(self)
        MEZCAL_MOTORES.__init__(self,None)
        BACKUP.__init__(self)

        self.queue = Queue.Queue()
        self.ds9=c_ds9.DS9("Mezcal")
        self.ds9.restart_iraf_cmd='./xmezcalds9iraf &'
        self.guiador=guiador2m_cliente.GUIADOR()
        #self.ds9.template="Mezcal"
        #print 'ds9 run'
        #self.ds9.run()
        self.numImg = 0
        self.numExp = 0000
        self.idExp = ""
        self.macro_file = None
        self.filter_file = None
        self.stop = False
        self.thread = None
        self.version=VERSION
        self.outfile="/imagenes/image1.fits"
        self.macros=c_mez_macros.MEZMACROS()
        self.set_timeout(1)
        self.old_lamp_state=0
        self.is_seq_open=False
        self.plate_scale=0.35369/2.0
        self.guiador_win_is_active=True
        self.caja_x=-1
        self.caja_y=-1
        self.is_auto_guiding=False


        lista_tiempo=[["t=0.1s",0.1],
        ["t=0.2s",0.2],
        ["t=0.5s",0.5],
        ["t=1.0s",1.0],
        ["t=2.0s",2.0],
        ["t=5.0s",5.0],
        ["t=10.0s",10.0],
        ["t=20.0s",20.0],
        ["t=30.0s",30.0]]

        lista_binx=[["X Binning=1",1],["X Binning=2",2],["X Binning=3",3],["X Binning=4",4]]
        lista_biny=[["Y Binning=1",1],["Y Binning=2",2],["Y Binning=3",3],["Y Binning=4",4]]

        self.lista_imagen=[["dark","d"],["flat","f"],["object","o"],["zero","b"],["arc","a"],["image",""],["movie",""]]
        self.STOP_secuencia=False
        self.imgtype='object'
        self.modo_mez='Image'
        self.is_exec_macro=False
        self.is_ccd_completed=False


        builder=gtk.Builder()
        builder.add_from_file("/usr/local/instrumentacion/Mezcal2014/mez.ui")
        #builder.connect_signals({"on_window1_destroy":gtk.main_quit})

        ######################################
        #aqui esta porque maneja parte grafica de platina
        GPLATINA.__init__(self,builder)
        ######################################
        builder.connect_signals(self)


        self.builder=builder
        self.window = builder.get_object("window2")
        self.window.connect("destroy", gtk.main_quit)
        ################## entry ccd ################################
        self.e_xorg = builder.get_object("e_xorg")
        self.e_yorg = builder.get_object("e_yorg")
        self.e_xsize = builder.get_object("e_xsize")
        self.e_ysize = builder.get_object("e_ysize")
        #ccd init
        self.b_ccd_init = builder.get_object("b_ccd_init")
        self.b_ccd_init.connect("clicked",self.on_b_ccd_init_clicked)
        ################## wheels ######################
        self.ew=[]
        for i in range(0,5):
            #print i
            este="entryw%d"%(i+1)
            #print este
            e=builder.get_object(este)
            self.ew.append(e)
            self.ew[i].set_text(self.lista_wheel[i])
        ################## slits ######################
        self.eslit=[]
        for i in range(0,3):
            #print i
            este="entrys%d"%(i+1)
            #print este
            e=builder.get_object(este)
            self.eslit.append(e)
            self.eslit[i].set_text(self.lista_rendijas[i])
        ################## filters ######################
        self.ef=[]
        for i in range(0,4):
            #print i
            este="entryf%d"%(i+1)
            #print este
            e=builder.get_object(este)
            self.ef.append(e)
            self.ef[i].set_text(self.lista_filtros[i])

        ################## COMBO Filtros ################################
        self.e_filtros = builder.get_object("l_filtros")
        self.ee_filtros = builder.get_object("eventboxfiltros")
        self.e_filtros.set_text("None")

        self.filtros = builder.get_object("c_filtros")
        #self.filtros.connect("changed",self.c_filtros_changed , 1)

        self.lfiltros=gtk.ListStore(gobject.TYPE_STRING)
        self.lfiltros.append(["Filters:"])

        for d in self.lista_filtros:
            #print "d=",d[0]
            self.lfiltros.append([d])

        self.filtros.set_model(self.lfiltros)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.filtros.pack_start(cell)
        self.filtros.add_attribute(cell, 'text', 0)
        #make the first row active
        self.filtros.set_active(0)
        ################## COMBO Wheel ################################
        self.e_wheel = builder.get_object("l_wheel")
        self.e_wheel.set_text("None")
        self.ee_wheel = builder.get_object("eventboxwheel")



        self.cwheel = builder.get_object("c_wheel")
        #self.cwheel.connect("changed",self.on_c_wheel_changed , 1)

        self.lwheel=gtk.ListStore(gobject.TYPE_STRING)
        self.lwheel.append(["Wheels:"])

        for d in self.lista_wheel:
            #print "d=",d[0]
            self.lwheel.append([d])

        self.cwheel.set_model(self.lwheel)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.cwheel.pack_start(cell)
        self.cwheel.add_attribute(cell, 'text', 0)
        #make the first row active
        self.cwheel.set_active(0)
        ################## COMBO slits o rendijas ################################
        self.e_slit = builder.get_object("l_slit")
        self.ee_slit = builder.get_object("eventboxslit")
        self.e_slit.set_text("None")


        self.cslit = builder.get_object("c_slit")
        #self.cslit.connect("changed",self.on_c_slit_changed , 1)

        self.lslit=gtk.ListStore(gobject.TYPE_STRING)
        self.lslit.append(["Slits:"])

        for d in self.lista_rendijas:
            #print "d=",d[0]
            self.lslit.append([d])

        self.cslit.set_model(self.lslit)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.cslit.pack_start(cell)
        self.cslit.add_attribute(cell, 'text', 0)
        #make the first row active
        self.cslit.set_active(0)

        ################## COMBO shutter ################################
        self.e_shutter = builder.get_object("e_shutter")
        self.b_open = builder.get_object("b_open")
        self.b_close = builder.get_object("b_close")
        self.e_shutter.set_text("Remote")

        self.c_shutter = builder.get_object("c_shutter")
        #self.c_shutter.connect("changed",self.on_c_shutter_changed , 1)

        self.lshutter=gtk.ListStore(gobject.TYPE_STRING)
        self.lshutter.append(["Remote"])
        self.lshutter.append(["Local"])



        self.c_shutter.set_model(self.lshutter)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.c_shutter.pack_start(cell)
        self.c_shutter.add_attribute(cell, 'text', 0)
        #make the first row active
        self.c_shutter.set_active(0)
        ################## COMBO lamp ################################
        self.b_lamp = builder.get_object("b_lamp")
        #self.e_lamp.connect("button_press_event",self.on_l_lamp_button_press_event,1)

        self.c_lamp = builder.get_object("c_lamp")
        #self.c_lamp.connect("changed",self.on_c_lamp_changed , 1)

        self.llamp=gtk.ListStore(gobject.TYPE_STRING)
        self.llamp.append(["Lamp:"])
        self.llamp.append([self.lista_lamparas[0]])
        self.llamp.append([self.lista_lamparas[1]])
        self.llamp.append([self.lista_lamparas[2]])



        self.c_lamp.set_model(self.llamp)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.c_lamp.pack_start(cell)
        self.c_lamp.add_attribute(cell, 'text', 0)
        #make the first row active
        self.c_lamp.set_active(0)
        ################## tiempo ################################
        #entry del tiempo
        self.e_tiempo = builder.get_object("e_tiempo")
        self.e_tiempo.set_text("0.1")
        #c_instrument
        self.tiempo = builder.get_object("c_tiempo")
        #self.tiempo.connect("changed",self.c_tiempo_changed , 1)

        self.ltiempo=gtk.ListStore(str,float)
        self.ltiempo.append( ["Exposure Time:",0.1] )
        for d in lista_tiempo:
            self.ltiempo.append([d[0],d[1]])

        self.tiempo.set_model(self.ltiempo)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.tiempo.pack_start(cell)
        self.tiempo.add_attribute(cell, 'text', 0)
        #make the first row active
        self.tiempo.set_active(0)
        ################## combo ccd ################################
        #etiqueta del ccd
        self.t_ccd = builder.get_object("l_ccd")
        self.l_ccdtxt=builder.get_object("l_ccdtxt")
        #ccd
        self.ccd = builder.get_object("c_ccd")
        #self.ccd.connect("changed",self.c_ccd_changed , 1)
        #lista del ccd
        self.lccd=gtk.ListStore(str,str)
        self.lccd.append(["CCD's:",""])
        for d in self.mi_ccd.mis_ccds:
            self.lccd.append([d[0],d[1]])

        self.ccd.set_model(self.lccd)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.ccd.pack_start(cell)
        self.ccd.add_attribute(cell, 'text', 0)
        #make the first row active
        #self.ccd.set_active(8) #ccd test
        self.ccd.set_active(4)  #marconi2


        ##################################################################
        ################## exposure ################################
        self.b_expone= builder.get_object("b_expone")
        self.cancela = builder.get_object("b_cancela")
        self.r_obj=builder.get_object("r_obj")
        self.r_obj.connect("toggled",self.on_itype_group_changed,"object")
        self.r_dark=builder.get_object("r_dark")
        self.r_dark.connect("toggled",self.on_itype_group_changed,"dark")
        self.r_bias=builder.get_object("r_bias")
        self.r_bias.connect("toggled",self.on_itype_group_changed,"zero")

        self.auto_save = builder.get_object("ck_automatic")


        ################## otros ################################
        self.basename = builder.get_object("e_base")
        self.directorio = builder.get_object("e_directorio")
        self.comentario = builder.get_object("e_comentario")
        self.ultima_imagen = builder.get_object("l_image")
        self.objetoid= builder.get_object("e_objetoid")

        self.fitcomment_frame = builder.get_object("hbox12")
        self.run_macro=builder.get_object("b_macro")
        self.observer = builder.get_object("e_observer1")
        self.observer2 = builder.get_object("e_observer")
        self.e_projectid = builder.get_object("e_proyectid")
        self.e_lens = builder.get_object("l_lens")
        self.e_lens.set_text("None")
        self.b_lens= builder.get_object("b_lens")
        #self.b_lens.set_sensitive(False)


        self.e_gratin = builder.get_object("l_grating")
        self.e_gratin.set_text("None")
        #self.b_gratin = builder.get_object("b_grating")
        self.frame_sec=builder.get_object("f_sec")
        self.frame_sec.hide()

        self.e_step=builder.get_object("e_sec_step")

        #self.e_posa=builder.get_object("e_posa")
        self.e_posl=builder.get_object("e_posl") #rotator angle
        self.e_posl2=builder.get_object("e_posl2") #PL
        self.e_ppa = builder.get_object("e_pa")    #PA


        self.b_exec_sec=builder.get_object("b_exec_sec")

        ################## diffuser ################################
        self.r_diffuser_in=builder.get_object("r_diff_in")
        self.r_diffuser_out=builder.get_object("r_diff_out")
        self.f_diffuser=builder.get_object("f_diffuser")

        ################## mirror ################################
        self.r_mirror_in=builder.get_object("r_mirr_in")
        self.f_mirror=builder.get_object("f_mirror")

        #self.r_mirror_in.connect("toggled",self.on_mirror_toggled,1)

        self.r_mirror_out=builder.get_object("r_mirr_out")
        #self.r_mirror_out.connect("toggled",self.on_mirror_toggled,2)

        #self.r_mirror_in.set_active(True)
        ################## c_xbin ################################
        self.xbin = builder.get_object("c_xbin")
        self.lxbin=gtk.ListStore(str,int)

        for d in lista_binx:
            self.lxbin.append([d[0],d[1]])

        self.xbin.set_model(self.lxbin)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.xbin.pack_start(cell)
        self.xbin.add_attribute(cell, 'text', 0)
        #make the first row active
        self.xbin.set_active(0)
        #self.xbin.connect("changed",self.c_xbin_changed, 1)
        ################## c_ybin ################################
        self.ybin = builder.get_object("c_ybin")
        self.lybin=gtk.ListStore(str,int)
        for d in lista_biny:
            self.lybin.append([d[0],d[1]])

        self.ybin.set_model(self.lybin)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.ybin.pack_start(cell)
        self.ybin.add_attribute(cell, 'text', 0)
        #make the first row active
        self.ybin.set_active(0)
        #self.ybin.connect("changed",self.c_ybin_changed, 1)

        ################## progressbar1 ################################
        self.barra = builder.get_object("progressbar1")
        self.barra.set_text("Progreso 0%")
        self.barra.show()
        self.barra.set_fraction(0)

        ################## textview1 ################################
        self.texto = builder.get_object("textview1")
        self.tbuffer=gtk.TextBuffer()
        self.texto.set_buffer(self.tbuffer)
        self.tbuffer.set_text("Almost Ready.... Waiting for CCD Response!!!!\n ")

        ################## textview2 ################################
        self.texto2 = builder.get_object("textview2")
        self.tbuffer2=gtk.TextBuffer()
        self.texto2.set_buffer(self.tbuffer2)
        #self.tbuffer2=self.texto2.get_buffer()
        self.tbuffer2.set_text("steps:\n ")
        self.tbuffer2.insert(self.tbuffer2.get_end_iter(),"hola\n ")

        self.win_seq_steps= builder.get_object("scrolledwindow2")
        self.win_seq_steps.hide()
        self.texto2.hide()


        #colores
        self.Tag_rojo = gtk.TextTag('rojo')
        self.Tag_rojo.set_property('background', 'red')
        self.Tag_verde = gtk.TextTag('verde')
        self.Tag_verde.set_property('background', 'green')
        self.Tag = gtk.TextTag('default')
        self.Tag.set_property('background', 'white')
        self.Tag_amarillo = gtk.TextTag('amarillo')
        self.Tag_amarillo.set_property('background', 'yellow')
        self.Tag_azul = gtk.TextTag('azul')
        self.Tag_azul.set_property('background', 'LightBlue')

        self.Tag_azul2 = gtk.TextTag('azul2')
        self.Tag_azul2.set_property('background', 'LightBlue')
        ################## botones Full frame y ds9 roi ################################
        self.full_frame = builder.get_object("b_full_frame")
        #self.full_frame.connect("clicked",self.on_full_frame_clicked)

        self.ds9roi = builder.get_object("b_ds9roi")
        #self.ds9roi.connect("clicked",self.on_ds9roi_clicked)

        self.roi2center=builder.get_object("b_roi2center")
        #self.roi2center.connect("clicked",self.on_b_roi2center_clicked)

        self.roi2roi=builder.get_object("b_roi2roi")
        #self.roi2roi.connect("clicked",self.on_b_roi2roi_clicked)



        ###########restart iraf y ds9
        self.restart = builder.get_object("b_restart")
        #self.restart.connect("clicked",self.on_b_restart_clicked)

        self.b_2pdf= builder.get_object("b_2pdf")
        #self.b_2pdf.connect("clicked",self.on_b_2pdf_clicked)

        ################## temperatura ################################
        self.temp = builder.get_object("b_temp")
        #self.temp.connect("clicked",self.on_b_temp_clicked)

        ################## combo sequencias ################################
        self.c_secuencias = builder.get_object("c_secuencias")
        self.lseq=gtk.ListStore(str)

        for d in self.macros.lista_nombres:
            #print d
            self.lseq.append( [d] )

        self.c_secuencias.set_model(self.lseq)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.c_secuencias.pack_start(cell)
        self.c_secuencias.add_attribute(cell, 'text', 0)
        #make the first row active
        self.c_secuencias.set_active(0)

        ################## lo del guiador ################################
        self.frame_guiador=builder.get_object('f_guiador')
        self.g_auto=builder.get_object('b_auto')


        self.g_image=builder.get_object('image2')

        self.g_image.set_size_request(192, 128)
        self.g_image.set_from_file('/tmp/img.pgm')
        self.g_image.connect("button-press-event", self.on_click)

        self.scrolledwindow=builder.get_object('scrolledwindow1')

        self.e_tiempo_guiador=builder.get_object('e_tiempo_guiador')

        self.move_guider_enable=builder.get_object("cb_move_guiador")
        self.move_guider_enable.set_active(1)


        # crear conexion de eventos del teclado para sacar menu escondido
        self.window.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.window.connect('key-release-event', self.on_key_press_event)


        #self.window_exit = builder.get_object("b_exit")
        #self.window_exit.connect("destroy", gtk.main_quit)



        #self.status.set_text('hola.......................')
        #self.inicio()

        #self.window.set_default_size(300,300)
        self.window.show()

        #cargar parametros de ambiente y archivo de configuracion
        self.do_main()
#------------------------------------------------------------------------------
    def do_main(self):
        print "en do_main..................................................."

        #cargar parametros anteriores
        self.params=c_ambiente2.AMBIENTE()
        #cargar parametros anteriores del ambiente y los pone en el menu de seleccion
        self.do_default()

        #configurar ds9,
        self.ds9.loadfile('/home/observa/Colorado/Mezcal2014/mezcal_portada.fits')
#------------------------------------------------------------------------------
    def on_b_exit_clicked(self, widget, data=None):
        print "saliendo del programa desde el window2"
        gtk.main_quit()
#------------------------------------------------------------------------------
    def on_b_continue_clicked(self, widget, data=None):
        print "main continue...."

        #mejor lo aranco con scrip y iraf
        #self.ds9.run()


        #esconder ventana de seleccion
        self.window.hide()
        #print "presionaron continue........................."
        self.main_window = self.builder.get_object("window1")
        self.main_window.connect("destroy", self.on_window_destroy)

        #crear conexion de eventos del teclado para sacar menu escondido
        #self.main_window.add_events(gtk.gdk.KEY_RELEASE_MASK)
        #self.main_window.connect('key-release-event', self.on_key_press_event)

        self.b_salida = self.builder.get_object("b_exit")
        self.b_salida.connect("clicked",self.on_window_destroy , 1)

        #parar la aimacion
        #self.throbber.set_from_pixbuf(self.pixbuf)

        #levantar ventana principal
        self.main_window.show()

        #esconder lo de los mensajes
        self.scrolledwindow.hide()
        self.main_window.resize(824,509)

        #guiador escondido
        self.frame_guiador.hide()
        self.guiador_win_is_active=False

        #guiador escondido ok
        #self.frame_guiador.show()
        #self.guiador_win_is_active=True

        #hacegurarnos que se mustra la ventana
        while gtk.events_pending():
                gtk.main_iteration()

        #configurar con lo seleccionado
        self.do_main_continue()

        #esperar a que cargue el ds9
        self.delay_gui_safe(2)

        #self.update_ccd_gui()



        #configurar ds9,
        try:
            self.ds9.do_init()
        except:
            print 'No pude hcer init de ds9'
        os.system('beep')

        #proyectid
        try:
            self.projectid=int(self.e_projectid.get_text())
        except:
            self.mi_ccd.mis_variables.mensajes('BAD Project ID',LOG,'rojo')
        else:
            self.mi_ccd.mis_variables.mensajes('Project ID %d'%self.projectid,LOG,'azul')
#------------------------------------------------------------------------------
    def do_main_continue (self):
        #ojo vamos a redefinir mi_ccd, a ver que pasa
        print "en do_main_continue ----------------------"

        ###### TIMERS #######
        self.timer_pos=time.time()

        print 'timer on...'
        if NOMEZCAL==False: self.update_pos_mezcal()    #tener las variables de una vez
        #timer in milisec
        if NOMEZCAL==False:
            gobject.timeout_add(1500,self.update_pos_mezcal)
        gobject.timeout_add(3000, self.update_pos_platina)

        #------------------------------------------------
        ccd=self.t_ccd.get_text()
        t="CCD: %s, Observer: %s, Instrumento: %s" % (ccd,self.observer.get_text(),'Mezcal')
        print t
        self.l_ccdtxt.set_text(ccd)
        self.main_window.set_title(ccd+" - IA-OAN-UNAM v"+str(VERSION)+" By. E. Colorado")
        self.cancela.set_sensitive(False)

        #verificar que CCD y cargar su clase
        print "estamos usando el ccd 7 por defaul, actual=",ccd

        if ccd=="e2vm":
            print "activando ccd Marconi"
            self.mi_ccd=c_ccd_marconi.CCD_MARCONI()
            #self.mi_ccd.set_ip(self.comm.host_marconi)
            #self.mi_ccd.set_puerto(self.comm.puerto_arranque)
            self.mi_ccd.ccd_info()
        elif ccd=="e2vm2":
            print "activando ccd Marconi2"
            self.mi_ccd=c_ccd_marconi2.CCD_MARCONI2()
            #self.mi_ccd.set_ip(self.comm.host_marconi)
            #self.mi_ccd.set_puerto(self.comm.puerto_arranque)
            self.mi_ccd.ccd_info()
        elif ccd=="e2vm3":
            print "activando ccd Marconi3"
            self.mi_ccd=c_ccd_marconi3.CCD_MARCONI3()
            self.mi_ccd.ccd_info()
        elif ccd=="e2vm4":
            print "activando ccd Marconi4"
            self.mi_ccd=c_ccd_marconi4.CCD_MARCONI4()
            self.mi_ccd.ccd_info()
        elif ccd=="TH7895":
            print "Start1"
            self.mi_ccd=c_ccd_star1.CCD_STAR1()
        elif ccd=="TH2K":
            print "Thompson 2K"
            self.mi_ccd=c_ccd_th2k.CCD_TH2K()
        elif ccd=="e2ve":
            print "activando ccd Esopo"
            self.mi_ccd=c_ccd_esopo.CCD_ESOPO()
        elif ccd=="SITE4":
            print "activando ccd SITE4"
            self.mi_ccd=c_ccd_site4.CCD_SITE4()
            self.ybin.set_sensitive(False)
        elif ccd=="SITE5":
            print "activando ccd Site5"
            self.mi_ccd=c_ccd_site5.CCD_SITE5()
            self.ybin.set_sensitive(False)
        elif ccd=="test":
            print "Test"
            self.mi_ccd=c_ccd_test.CCD_TEST()
        elif ccd=="fli":
            print "Fli"
            self.mi_ccd=c_ccd_fli.CCD_FLI()
            self.box_fli.show()
            #esconde otro meno de ccd output
            self.frame_output.hide()
            self.fli_menu()
        elif ccd=="sbig":
            print "SBIG"
            self.mi_ccd=c_ccd_sbig2.SBIG2()
            self.box_sbig.show()
            #esconde otro meno de ccd output
            self.frame_output.hide()
            self.ybin.set_sensitive(False)
            #quitar el binning 4
            del self.lxbin[-1]
        elif ccd=="TH7896":
            print "CCD Mil Tona"
            self.mi_ccd=c_ccd_mil.CCD_MIL()
        elif ccd=="SPECTRAL":
            print "Activando CCD Spectral"
            self.mi_ccd=c_ccd_spectral.CCD_SPECTRAL()
            self.rotate_axis = True
            #self.box_spec.show()
        elif ccd=="SPECTRAL2":
            print "Activando CCD Spectral 2"
            self.mi_ccd=c_ccd_spectral_2.CCD_SPECTRAL_2()
            self.rotate_axis = True

            #self.box_spec.show()
        else:
            print "no encontre CCD"

        print 'aqui m2'
        #secundario y telescopio
        telescope = "2.12m"
        self.mi_ccd.cambia_telescopio(telescope) #no funciona electronica del Fer
        #escala de placa
        self.mi_ccd.cambia_escala_placa(telescope,ccd)
        #signos por salida del CCD
        self.mi_ccd.decscale=self.mi_ccd.arscale=self.plate_scale




        #actualizar algunas variables
        if self.mi_ccd.can_readtemp == False:
            self.temp.set_sensitive(False)

        self.observerb2f = self.observer.get_text()
        self.observerb2f=self.observerb2f.replace(',',';')  #sin comas para log
        self.observer2.set_text(self.observer.get_text())




        self.tel = "2.12m"
        self.instrument = "Mezcal"



        #para los colores de los mensajes
        self.tbuffer.get_tag_table().add(self.Tag_rojo)
        self.tbuffer.get_tag_table().add(self.Tag_verde)
        self.tbuffer.get_tag_table().add(self.Tag)
        self.tbuffer.get_tag_table().add(self.Tag_amarillo)
        self.tbuffer.get_tag_table().add(self.Tag_azul)
        #2
        #self.Tag_azul2=self.Tag_azul
        self.tbuffer2.get_tag_table().add(self.Tag_azul2)
        #clima
        self.mi_ccd.weather_enable=True
        #self.mi_ccd.server='132.248.4.66'


        #inicializar CCD
        self.mi_ccd.mis_variables.queue = self.queue
        self.mi_ccd.mis_variables.mensajes(t)

        self.colorBotones()
        self.estadoBotones(False)
        ##################################################
        #gobject.timeout_add(25,self.procesaMensaje)

        gobject.timeout_add(10,self.procesaMensaje)


        ithread = threading.Thread(target=self.mi_ccd.inicializa)
        ithread.start()
        #self.mi_ccd.inicializa()




        ################################################
        #ya esta todo deninido, poner aqui lo automatico


        #esperar thread de inicializacion
        print "************ Esperando Thread de Inicializacion *******************"
        #ithread.join()
        #if ithread!=None and ithread.isAlive():
        while  ithread.isAlive():
            while gtk.events_pending(): gtk.main_iteration()
            print "."
            time.sleep(0.1)

        self.update_ccd_gui()
        self.estadoBotones(True)

        #mas update mirror y difusser
        print 'update mirror status'

        if self.diffuser:
            self.r_diffuser_in.set_active(True)
        else:
            self.r_diffuser_out.set_active(True)

        if self.mirror:
            self.r_mirror_in.set_active(True)
        else:
            self.r_mirror_out.set_active(True)


        #cargar otros parametros anteriores
        try:
            self.do_load_last_parms()
        except:
            self.mi_ccd.mis_variables.mensajes("Unable to load last session parameters","Log","amarillo")

        #botones
        self.filtros.set_sensitive(True)
        self.cwheel.set_sensitive(True)
        self.cslit.set_sensitive(True)

        if ccd=="e2vm2":
                print "activando ccd Marconi2 CANAL LEFT"
                self.mi_ccd.ccd_info()
                #2016, cambiar salida default
                print "**** 2016 Voy a cambiar salida LEFT *******"
                self.mi_ccd.output=['Left', 1]
                self.mi_ccd.output_actual=1
                self.mi_ccd.cambia_salida()
                self.mi_ccd.ccd_info()
                #cambio de escala
                self.mi_ccd.decscale=-1*self.plate_scale
                #self.mi_ccd.arscale=-1*self.plate_scale
        elif ccd=="SPECTRAL2":
            print "activando ccd Espectral2 para mezcal"
            self.mi_ccd.arscale=  self.plate_scale*-1

        elif ccd=="SPECTRAL":
            print "activando ccd Espectral 1 para mezcal"
            self.mi_ccd.arscale=  -self.plate_scale
            self.mi_ccd.decscale = +self.plate_scale

        self.mi_ccd.ccd_ready=True
        self.is_ccd_completed = True
        print "************ Termine Do Main Continue  *******************"
############################################################################
    def on_window_destroy(self, widget, data=None):
        print "**************************** Vamos a Salir..... **********************************************************"
        self.mi_ccd.stop=True
        self.stop = True

        #actualizar variables de ambiente
        self.params.var['CCD_OBSERVER']=self.observer.get_text()
        self.params.var['CCD_BASE']=self.basename.get_text()
        #self.params.var['CCD_INSTRUMENT']=self.e_instrument.get_text()
        self.params.var['CCD_CCD']=self.t_ccd.get_text()
        self.params.var['CCD_OBJECT']=self.objetoid.get_text()
        self.params.var['CCD_WDIR']=self.directorio.get_text()
        self.params.var['CCD_LAST']=self.ultima_imagen.get_text()
        #V4.19
        self.params.var['CCD_BINN']=str(self.mi_ccd.cbin)+' '+str(self.mi_ccd.rbin)
        self.params.var['CCD_XORG']=self.e_xorg.get_text()
        self.params.var['CCD_YORG']=self.e_yorg.get_text()
        self.params.var['CCD_XSIZE']=self.e_xsize.get_text()
        self.params.var['CCD_YSIZE']=self.e_ysize.get_text()

        nombre=self.macros.lista_nombres[self.c_secuencias.get_active()]
        self.params.var['CCD_MACRO']=nombre
        del self.params

        self.ds9.terminate()
        print "matando clase ccd"
        try:
            del self.mi_ccd
        except:
            print "algo paso, no pude borrar clase ccd"
        gtk.main_quit()
############################################################################
    def c_filtros_changed(self, widget, data=None):
        print 'cambio filtros'

        model=self.filtros.get_model()
        index=self.filtros.get_active()
        #print "model",model
        #print "index",index

        if not (index>0):
            return -1

        widget.set_sensitive(False)
        self.ee_filtros.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        while gtk.events_pending(): gtk.main_iteration()
        #vamos a mover rueda de filtros
        self.e_filtros.set_text(model[index][0])


        self.is_moving+=1
        self.mueve(self.eje_filtro,index-1)
        self.espera_filtros(index-1)
        self.is_moving-=1

        #self.filtros.set_active(0)
############################################################################
    def on_c_wheel_changed(self, widget, data=None):

        #model=widget.get_model()
        index=widget.get_active()
        print index
        if not (index>0):
            return -1

        widget.set_sensitive(False)
        self.ee_wheel.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        print "cambio wheels",index
        self.is_moving+=1
        self.mueve(self.eje_wheel,index-1)
        self.espera_wheel(index-1)
        self.is_moving-=1
############################################################################
    def on_c_slit_changed(self, widget, data=None):

        #model=widget.get_model()
        index=widget.get_active()
        print 'slits index',index

        if not (index>0):
            print 'No escojiste posicion de slits, no voy hacer nada'
            return -1
        widget.set_sensitive(False)
        self.cambia_slit(index-1)

############################################################################

    def cambia_slit(self,pos):
        self.ee_slit.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        print "cambio slits",pos
        self.is_moving+=1
        self.mueve(self.eje_rendija,pos)

        self.espera_slit(pos)
        self.is_moving-=1

############################################################################
    def on_c_shutter_changed(self, widget, data=None):

        #model=widget.get_model()
        index=widget.get_active()
        #print model,index
        #remote 0
        #local 1
        if index==0:
            print 'shutter modo remoto'
            self.e_shutter.set_text("Remote")
            #deshabilitar botones
            self.b_close.set_sensitive(False)
            self.b_open.set_sensitive(False)
            self.e_shutter.set_sensitive(False)
            self.deshabilita_shutter()
        else:
            print 'shutter modo local'
            self.e_shutter.set_text("Local")
            self.b_close.set_sensitive(True)
            self.b_open.set_sensitive(True)
            self.e_shutter.set_sensitive(True)
            self.habilita_shutter()


############################################################################
    def c_tiempo_changed(self, widget, data=None):
        model=self.tiempo.get_model()
        index=self.tiempo.get_active()
        t=0.1
        if index:
            t=model[index][0]
            print t,'selected', "valor int=",model[index][1]
        #cambiar la etiqueta
        if index>0 :
            self.e_tiempo.set_text(str(model[index][1]))
            self.mi_ccd.etime=model[index][1]

        self.tiempo.set_active(0)
############################################################################
    def update_mes_gui(self):
        #print 'updating mes gui'
        self.e_wheel.set_text(self.lista_wheel[self.wheel])
        self.e_filtros.set_text(self.lista_filtros[self.filtro])
        self.e_slit.set_text(self.lista_rendijas[self.slit])
        self.e_shutter.set_text(self.shutter)
        self.e_gratin.set_text(str(self.rejilla_mes))
        self.e_lens.set_text(str(self.lentes_mes))

        if self.estado_lamp==1:
            #lamparas apagadas
            self.b_lamp.set_label(self.lista_lamparas[0])
        else:
            self.b_lamp.set_label(self.lista_lamparas[self.lamp])
        #.set_text()
        while gtk.events_pending(): gtk.main_iteration()

        if self.seguro_foco==1:
            #esta con seguro
            self.b_lens.set_sensitive(False)
        else:
            self.b_lens.set_sensitive(True)
############################################################################
    def on_b_lamp_clicked(self, widget, data=None):
        print "boton lamparas"
        #self.r_mirror_in.set_active(False)
        #self.on_mirror_toggled(self.r_mirror_in,2)
        #r=self.pide_posicion()
        #if r >0 : self.update_mes_gui()
        #self.mezcal_info()

        #checar etiqueta del boton
        label=self.b_lamp.get_label()
        print 'etiqueta', label



        print 'index antes',self.old_lamp_state

        if label!=self.lista_lamparas[0]:
            #off

            if label==self.lista_lamparas[1]:
                #Tungsten
                self.old_lamp_state=1
            elif label==self.lista_lamparas[2]:
                #Th - Ar
                self.old_lamp_state=0

            print 'lamp prendida, voy a apagar, index antes',self.old_lamp_state
            #mandar a apagar
            self.apaga()
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        else:
            print 'voy a encender lamapara con index',self.old_lamp_state
            self.enciende(self.old_lamp_state)
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))





        '''
        self.is_moving+=1
        if self.is_moving > 0:
            self.b_lamp.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))
            self.b_lamp.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
            self.is_moving=-1
        else:
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
            self.b_lamp.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
            self.b_lamp.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
            self.b_lamp.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))

            self.b_lamp.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("blue"))
            self.b_lamp.modify_base(gtk.STATE_ACTIVE, gtk.gdk.color_parse("blue"))
            self.b_lamp.modify_fg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("blue"))
        '''

    ############################################################################
    def on_key_press_event(self, widget, event, *args):
        keyname = gtk.gdk.keyval_name(event.keyval).upper()

        # if event.state & gtk.gdk.SHIFT_MASK :


        if event.state & gtk.gdk.CONTROL_MASK:
            if keyname == 'F':
                print "CTRL + Menu secreto del FOCO "
                rect = self.main_window.allocation
                pos = self.main_window.get_position()
                print pos
                self.extra_window.show()
                self.extra_window.move(pos[0] + rect.width + 10, pos[1])
            if keyname == 'T':
                print "CTRL + Threads info "
                # verificar threads

                txt = 'Header is alive? ' + str(self.thread.isAlive())
                print txt
                self.mi_ccd.mis_variables.mensajes(txt, "Log", "verde")

                txt = 'contadores activos= ' + str(threading.activeCount())
                print txt
                self.mi_ccd.mis_variables.mensajes(txt, "Log", "verde")

                txt = 'lista threads= ' + str(threading.enumerate())
                print txt
                self.mi_ccd.mis_variables.mensajes(txt, "Log", "verde")

                txt = 'Expone is alive? ' + str(self.thread2.isAlive())
                print txt
                self.mi_ccd.mis_variables.mensajes(txt, "Log", "verde")



            if keyname == 'Z':
                print "CTRL + Z Menu secreto de Astrometry "


############################################################################
    def on_mirror_toggled(self, widget, data=None):
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        self.f_mirror.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        print "Mirror output changed ",data
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])


        activo=widget.get_active()
        print "activo",activo

        self.is_moving+=1
        if activo==True:
            print "do_mirror in"
            self.espejo_in()
            self.espera_mirror(1)
        else:
            print "do_mirror out"
            self.espejo_out()
            self.espera_mirror(0)

        self.f_mirror.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.is_moving-=1
############################################################################
    def on_diffuser_toggled(self, widget, data=None):
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        self.f_diffuser.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        while gtk.events_pending(): gtk.main_iteration()
        print "Diffuser output changed ",data
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])


        activo=widget.get_active()
        print "activo",activo

        self.is_moving+=1
        if activo==True:
            print "difusser in"
            self.difusor_in()
            self.espera_difusor(1)
        else:
            print "diffuser out"
            self.difusor_out()
            self.espera_difusor(0)

        self.is_moving-=1
        self.f_diffuser.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
############################################################################
    def espera_difusor(self,pos):
        print 'esperando difusor mezcal'

        ok=True
        r=1
        while ok:
            self.delay_gui_safe(1)
            if self.diffuser==pos:
                print "ya llego difusor..."
                ok=False
            self.check_pos_timer()
############################################################################
    def espera_mirror(self,pos):
        print 'esperando mirror mezcal'

        ok=True
        r=1
        while ok:
            self.delay_gui_safe(1)
            if self.mirror==pos:
                print "ya llego mirror..."
                ok=False
            self.check_pos_timer()
############################################################################
    def espera_filtros(self,pos):
        print 'esperando filtros mezcal'

        ok=True
        r=1
        mytimer=time.time()
        timeout=60
        while ok:
            #while gtk.events_pending(): gtk.main_iteration()
            #time.sleep(1)
            self.delay_gui_safe(1)
            if self.filtro==pos:
                print "ya llego filtro..."
                ok=False
            else: print 'no ha llegado filtro'
            self.check_pos_timer()
            t=time.time()-mytimer
            if t >timeout:
                print "Timeout en Eje Filter"
                self.mi_ccd.mis_variables.mensajes("TimeOut en Eje Filter",LOG,'red')
                break

        self.ee_filtros.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.filtros.set_sensitive(True)
############################################################################
    def espera_slit(self,pos):
        print 'esperando slits mezcal'

        ok=True
        r=1
        mytimer=time.time()
        timeout=60
        while ok:
            #while gtk.events_pending(): gtk.main_iteration()
            #time.sleep(1)
            self.delay_gui_safe(1)
            if self.slit==pos:
                print "ya llego slits..."
                ok=False
            else: print "No ha llegodo slit "
            self.check_pos_timer()
            t=time.time()-mytimer
            if t >timeout:
                print "Timeout en Eje Slits"
                self.mi_ccd.mis_variables.mensajes("TimeOut en Eje Slits",LOG,'red')
                break

        self.ee_slit.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.cslit.set_sensitive(True)
############################################################################
    def espera_wheel(self,pos):
        print 'esperando wheel mezcal'

        ok=True
        r=1
        conta=0
        mytimer=time.time()
        timeout=60
        while ok:
            #while gtk.events_pending(): gtk.main_iteration()
            #time.sleep(1)
            conta+=1
            self.delay_gui_safe(2)
            if self.wheel==pos:
                print "ya llego wheel..."
                ok=False
            else: print "No ha llegodo wheel ",conta
            self.check_pos_timer()

            t=time.time()-mytimer
            if t >timeout:
                print "Timeout en Eje Wheel"
                self.mi_ccd.mis_variables.mensajes("TimeOut en Eje Wheel",LOG,'red')
                break


        self.ee_wheel.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.cwheel.set_sensitive(True)
############################################################################
    def check_pos_timer(self):
        max_delay=5
        if time.time() > (self.timer_pos+max_delay):
                print '******************************************************'
                print 'Hey no has pedido el estatus en mas de %d seg'%max_delay
                self.update_pos_mezcal()
                print '******************************************************'

############################################################################
    def update_pos_mezcal(self):

        #pedir estado de mezcal
        r=-1
        if not self.busy:
            try:
                r=self.pide_posicion()
            except:
                print 'Error al pedir posicion',r

            if r >0 :
                self.timer_pos=time.time()
                self.update_mes_gui()
        else : print "******* MEZCAL BUSY *********"


        ################
        #e=o ok, e=-1 error
        e=self.checa_errores()
        if e==1:
            pass
        elif e==-1:
            self.mi_ccd.mis_variables.mensajes("**** Error de conexion de Red ****",LOG,'red')
        elif e==-2:
            #hay error
            print 'e=',e
            self.mi_ccd.mis_variables.mensajes(self.error_mezcal,LOG,'red')
            if self.error_mez_contador ==1:
                #pintar ventana una sola vez
                print 'primer error detectado'
                self.show_error('Error en Electronica de Mezcal: '+self.error_mezcal)
                self.error_mez_contador+=1




        ################
        '''
        r=self.pide_posicion()
            #print 'r',r
        if r >0 : self.update_mes_gui()
        '''
        return True

############################################################################
    def update_pos_platina(self):
        
        try:
            ok=self.platina.estado()
        except:
            print 'no pude leer platina'
            ok=False

        if ok:
            self.e_posl.set_text(str(self.platina.angulo)) #rotator angle
            self.e_posl2.set_text(str(self.platina.angulo))
    
            pa=self.platina.PL_2_PA(self.platina.angulo)
            #print 'angulo',self.platina.angulo,'pa',pa,'pa2',self.platina.PA2
            try:
                t='%3.2f , %3.2f'%(pa,self.platina.PA2)
            except:
                return True
            #print t
    
            self.e_ppa.set_text(t)

        return True
    ############################################################################
    def on_c_lamp_changed(self, widget, data=None):
        index=widget.get_active()
        if not (index>0):
            return -1
        print "cambio lamp",index
        if index==1:
            print 'apagar lampara'
            self.apaga()
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        elif index==2:
            print "enciende Tungsten"
            self.enciende(1)
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))
        elif index==3:
            print "enciende Th-Ar"
            self.enciende(0)
            self.b_lamp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))

        widget.set_active(0)
############################################################################
    def c_xbin_changed (self, widget, data=None):
        print "cambio x bin"
        model=self.xbin.get_model()
        index=self.xbin.get_active()
        t=model[index][0]
        self.mi_ccd.cbin=model[index][1]
        print t,'selected','g=',self.mi_ccd.cbin
        ######################
        '''
        if not self.mi_ccd.bin_n_roi and self.mi_ccd.cbin >1:
            print "Roi Disable"
            self.ds9roi.set_sensitive(False)
        else:
            self.ds9roi.set_sensitive(True)
        '''
        ######################
        ccd=self.t_ccd.get_text()
        if ccd == "SITE4" or ccd == "SITE5" or ccd == "sbig" or ccd == "TH2K" or ccd == "TH7896":
            self.ybin.set_active(index)
            self.mi_ccd.rbin=model[index][1]
            self.mi_ccd.bin=model[index][1]
        self.mi_ccd.full_frame()
        self.update_ccd_gui()
############################################################################
    def c_ybin_changed (self, widget, data=None):
        print "cambio y bin"
        model=self.ybin.get_model()
        index=self.ybin.get_active()
        #print "model",model
        #print 'index',index
        self.mi_ccd.rbin=model[index][1]
        #print model[index][0],'selected','g=',self.mi_ccd.rbin
        self.mi_ccd.full_frame()
        #actualizar valores en gui
        self.update_ccd_gui()
############################################################################
    def update_ccd_gui(self):
        #poner valores en gui
        self.e_xorg.set_text(str(self.mi_ccd.xorg))
        self.e_yorg.set_text(str(self.mi_ccd.yorg))
        self.e_xsize.set_text(str(self.mi_ccd.xsize))
        self.e_ysize.set_text(str(self.mi_ccd.ysize))
        self.e_tiempo.set_text(str(self.mi_ccd.etime))

        while gtk.events_pending(): gtk.main_iteration()
############################################################################
    def on_b_lens_clicked(self, widget, data=None):
        print "boton lenses presionado",data
        clave='mezcal.5345'
        dialog=gtk.Dialog(title="Move Lens",parent=self.main_window,flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        #,buttons=('Move',1)

        label2=gtk.Label("Enter Supervisor Password:")
        dialog.vbox.pack_start(label2,True,True,0)
        label2.show()

        ep=gtk.Entry()
        dialog.vbox.pack_start(ep,True,True,0)
        ep.show()

        label=gtk.Label("Enter the position:")
        dialog.vbox.pack_start(label,True,True,0)
        label.show()

        valor=self.e_lens.get_text()
        e=gtk.Entry()
        dialog.vbox.pack_start(e,True,True,0)
        e.show()
        #poner valor
        e.set_text(valor)

        dialog.add_button('Move',1)
        response = dialog.run()
        print "response",response

        d=e.get_text()
        p=ep.get_text()
        print 'tengo=',d
        if response <0:
            print "destruyeron mi ventana"

        dialog.destroy()

        print 'clave',p,len(p),len(clave)


        if p!=clave:
            self.mi_ccd.mis_variables.mensajes("Bad Password!","Log","rojo")
            return

        try:
            m=int(d)
            print "voy a mover lentes"
            self.mueve_lentes(m)
        except:
            print "Hubo error en adquirir dato"
############################################################################
    def on_b_grating_clicked(self, widget, data=None):
        print "boton gratin presionado"
	return
        dialog=gtk.Dialog(title="Move Gratin",parent=self.main_window,flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        #,buttons=('Move',1)
        label=gtk.Label("Enter the position:")
        dialog.vbox.pack_start(label,True,True,0)
        label.show()


        #leer valor que tiene
        valor=self.e_gratin.get_text()
        e=gtk.Entry()
        dialog.vbox.pack_start(e,True,True,0)
        e.show()
        #poner valor
        e.set_text(valor)

        dialog.add_button('Move',1)
        response = dialog.run()
        print "response",response

        d=e.get_text()
        print 'tengo=',d
        if response <0:
            print "destruyeron mi ventana"

        dialog.destroy()
        try:
            m=int(d)
            print "voy a mover Gratin"
            #self.e_grating.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
            self.mueve_rejilla(m)
        except:
            print "Hubo error en adquirir dato"
############################################################################
    def c_ccd_changed(self, widget, data=None):
        model=self.ccd.get_model()
        index=self.ccd.get_active()
        if index:
            t=model[index][0]
            v=model[index][1]
            print t,v
        #cambiar la etiqueta
        if index>0 :
            self.t_ccd.set_text(v)
############################################################################
    def on_b_temp_clicked(self, widget, data=None):
        self.mi_ccd.get_temp()
        #cambiar etiqueta al boton
        txt="T= "+str(self.mi_ccd.temp)
        self.temp.set_label(txt)
        self.checa_temp()
############################################################################
    def on_expone_clicked(self, data,index=1,modo=None):
        print "Vamos a exponer.............................................."
        #print 'data=',data,' index=',index

        if modo==None:
            self.modo_mez='Image'

        self.mi_ccd.tam_binario=0
        self.stop = False
        self.mi_ccd.ccd_ready=False
        self.is_ccd_completed = False
        self.estadoBotones(False)
        self.mi_ccd.stop=False


        #hacer los pre expone****
        #self.checa_comas()  #que las bitacora no use comas

        #hacer thread the header
        #print "voy a hacer thread"
        #header
        #print "tiempo de integracion=",self.mi_ccd.etime
        self.saca_datos_gui()
        #print "2 tiempo de integracion=",self.mi_ccd.etime

        #por si no hay rueda de filtros, poner la info del gui
        #self.mi_ccd.mi_filtro.filtro=self.e_filtros.get_text()

        #es el pre-header
        self.thread = threading.Thread(target=self.guarda_header)
        self.thread.start()

        #preparar para exponer
        #if DEBUG: print "index=",index
        #tipos
        #self.imgtype=self.lista_imagen[index][0]
        #if DEBUG: print "tipo=",self.imgtype
        #if DEBUG: print "id=",self.lista_imagen[index][1]
        if self.imgtype=='dark':
            index=0
        elif self.imgtype=='object':
            index=2
        elif self.imgtype=='zero':
            index=3
        self.idExp = self.lista_imagen[index][1]
        #print "idExp",self.idExp

        #actualizar estado del shutter
        if self.imgtype=='zero' or self.imgtype=='dark':
            if DEBUG: print "shutter cerrado"
            self.mi_ccd.shutter=0
        else:
            if DEBUG: print "shutter abierto"
            self.mi_ccd.shutter=1

        #cuidar tiempo de integracion cuando sea bias
        if self.imgtype=='zero':
            if DEBUG: print "es BIAS"
            self.mi_ccd.etime=0
        elif self.mi_ccd.etime==0: self.mi_ccd.etime=0.1

        #actualizar tiempo en gui
        self.update_ccd_gui()

        #######
        self.pre_expone()
        #######

        #exponer
        self.thread2 = threading.Thread(target=self.mi_ccd.expone)
        self.thread2.start()
        #esperar imagen cuando no sea busy
        while gtk.events_pending():
                gtk.main_iteration()

        time.sleep(0.5)
        self.espera_ccd(data)
        print "FIN de Exponer ......................................"
        #verificar threads
        '''
        print "tread header"
        print 'is alive',self.thread.isAlive
        print 'contador activos',threading.activeCount()
        print 'lista threads',threading.enumerate()
        print "tread expone"
        print 'is alive',self.thread2.isAlive
        '''
        print "///////////////////////////////////////////////////////////"
        print "///////////////////////////////////////////////////////////"
        print "///////////////////////////////////////////////////////////"
        self.is_ccd_completed = True
############################################################################
    def actualizaBarra (self,tfinal):
        progreso = 0
        tini = time.time()
        self.mi_ccd.update_barra("t "+str(progreso)+" de "+str(tfinal),0)
        self.mi_ccd.update_barraColor('blue')
        while progreso<100:
            if self.stop:					#verifica si se presiono Cancelar
                print "Tiempo de exposicion Cancelado"
                break
            tactual = time.time()-tini			#tiempo transcurrido
            if tfinal>0:
                progreso = tactual*100/tfinal		#porcentaje del progreso total
            mensaje="t = %.1fs de %ss "%(tactual,tfinal)
            self.mi_ccd.update_barra(mensaje,progreso)
            while gtk.events_pending():
                gtk.main_iteration()
        print "Tiempo de Exposicion "+str(progreso)+"%"
############################################################################
    def espera_ccd (self,data):
        print "Espera ccd general........................."

        #hacer ciclo de pide estatus
        if self.mi_ccd.stop: self.stop=True
        tim = float(self.e_tiempo.get_text())

        if self.stop == False:
            print "En Espera de podernos traernos los datos !!!!!!!!!!!!!!!"
            resp=self.mi_ccd.espera_estatus(tim)
            if resp:
                print "Ya podernos traernos los datos !!!!!!!!!!!!!!!"
                self.mi_ccd.trae_binario()
                if data=='fli_dark':
                    print 'do display para fli ..........'
                    self.do_display_flidark()
                else:
                    #print 'do display Normal  ..........'
                    self.do_display()
                self.post_expone()
                self.upgrade_fits_mezcal()
            else:
                print 'Me cancelaron durante exposicion'

        else:
            print "esta stop TRUE, me cancelaron xxxxxxxxxxxxxxxxxxxxxx"
        time.sleep(0.5)
        if not self.is_exec_macro:
            self.estadoBotones(True)

        print "FIN Espera ccd general........................."
############################################################################
    def do_display(self):
        if self.stop==False:    #verifica si se presiono Cancelar
            #print "en do display"
            inicio= time.clock()
            if self.imgtype=='image' or self.imgtype=='movie':
                self.numImg+=1
                dir = "/imagenes/"
                imagen = "image"+str(self.numImg)+".bin"
                imagen = os.path.join(dir,imagen)
                if self.numImg == 5: self.numImg = 0
            else:
                dir = self.directorio.get_text()
                #anexar path defaul imagenes
                dir = os.path.join('/imagenes/',dir.strip())
                if os.path.exists(dir) == False:
                    os.makedirs(dir)
                ultima,numero=self.busca_archivo(dir,self.basename.get_text().strip())
                self.numExp = int(numero)+1
                numero = "%.4d" %self.numExp
                imagen = self.basename.get_text().strip()+numero+self.idExp
                imagen = os.path.join(dir,imagen)
            #que no exista
            self.checa_es_archivo(dir,self.basename.get_text().strip(),imagen+".fits")

            image = imagen.split('.')
            basename = image[0]
            #print basename
            self.outfile=basename+".fits"
            print "vamos a generar fits, %s, (%d x %d)"%(self.outfile,self.mi_ccd.xsize,self.mi_ccd.ysize)
            self.crear(self.mi_ccd.bindata,self.mi_ccd.xsize,self.mi_ccd.ysize, self.outfile)
            final= time.clock()
            tiempo= final-inicio
            if DEBUG: print "tarde %f segundos en bin2fits"%tiempo
            #desplegar en ds9
            self.mi_ccd.mis_variables.mensajes("Image >"+self.outfile+" Done!.....","Log","verde")
            self.ds9.loadfile(self.outfile)
            img = os.path.basename(self.outfile)
            self.ultima_imagen.set_text(img)

            #Configurar el DS9 la primera vez
            if self.mi_ccd.is_first_image:
                self.mi_ccd.is_first_image=False
                #self.mi_ccd.setup_first_image()
                self.mis_variables.mensajes("Setting DS9 defaults for Test",Color="verde")
                #self.ds9.set_mando(" scale zcale")
                self.ds9.set_mando(" scale log")
                self.ds9.set_mando(" zoom to fit")
                if self.t_ccd.get_text()=="SPECTRAL2":
                    print 'DS9 ya orientado con spectral2'
                else:
                    self.ds9.set_mando(" orient y")
                    self.ds9.set_mando(" rotate 90")

############################################################################
    def estadoBotones(self,estado):
        self.b_expone.set_sensitive(estado)
        #self.b_close.set_sensitive(estado)
        #self.b_open.set_sensitive(estado)
        #self.e_shutter.set_sensitive(estado)

        self.e_xorg.set_sensitive(estado)
        self.e_yorg.set_sensitive(estado)
        self.e_xsize.set_sensitive(estado)
        self.e_ysize.set_sensitive(estado)

        self.b_lamp.set_sensitive(estado)
        self.c_lamp.set_sensitive(estado)
        self.full_frame.set_sensitive(estado)
        self.ds9roi.set_sensitive(estado)
        self.roi2center.set_sensitive(estado)
        self.roi2roi.set_sensitive(estado)
        self.temp.set_sensitive(estado)
        self.c_secuencias.set_sensitive(estado)
        self.b_exec_sec.set_sensitive(estado)
        self.xbin.set_sensitive(estado)
        self.ybin.set_sensitive(estado)


        #self.image.set_sensitive(estado)
        #self.dark.set_sensitive(estado)
        #self.objecto.set_sensitive(estado)
        #self.flat.set_sensitive(estado)
        #self.arc.set_sensitive(estado)
        #self.movie.set_sensitive(estado)
        self.cancela.set_sensitive(not(estado))
        '''
        if self.macro_file is None:
            self.run_macro.set_sensitive(False)
        else:
            self.run_macro.set_sensitive(estado)
        '''
############################################################################
    def on_cancela_clicked (self, widget, data=None):
        print '\n\n******************* CANCEL **********************\n\n'
        self.mi_ccd.mis_variables.mensajes("vamos a CANCELAR","Log","rojo")
        self.mi_ccd.stop=True
        self.stop = True
        self.mi_ccd.cancela()
        #hacer pequeno delay para que todo se destruya bien
        time.sleep(1)
        self.estadoBotones(True)
        print 'Cancel finished ...'
############################################################################
    def colorBotones(self):
        self.cancela.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        self.temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))
        #self.load_macro.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
        self.run_macro.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
        self.full_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
        self.fitcomment_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))

        self.cancela.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("red"))
        self.temp.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("yellow"))
        #self.load_macro.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("green"))
        self.run_macro.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("green"))
        self.full_frame.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("gray"))
        self.fitcomment_frame.modify_bg(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("yellow"))
        self.b_2pdf.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("NavajoWhite"))

        self.e_gratin.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
############################################################################
    def on_b_macro_clicked(self , widget, data=None):
        print 'Sequencias'



        if self.is_seq_open:
            #vamos a cerrar
            print "Cerrando secuencias"
            self.frame_sec.hide()
            self.texto2.hide()
            self.win_seq_steps.hide()
            self.is_seq_open=False
            self.main_window.resize(824,400)
            self.run_macro.set_label('Open Sequences')

        else:
            #vamos abrir
            print "Abriendo secuencias"
            self.frame_sec.show()
            self.win_seq_steps.show()
            self.texto2.show()

            #falta hacer grande la Ventana, orig 812x710
            #self.main_window.set_size_request(812, 710)
            self.main_window.resize(824,600)
            self.is_seq_open=True
            self.run_macro.set_label('Close Sequences')


############################################################################
    def checa_temp(self):
        #lo del los colores del boton de temperatura
        if self.mi_ccd.can_readtemp==True:
            #print "temp=%f (%f,%f)"% (self.mi_ccd.temp,self.mi_ccd.temp_lowlimit,self.mi_ccd.temp_hilimit)


            if (self.mi_ccd.temp <= self.mi_ccd.temp_hilimit):
                self.temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
                #print 'verde'
            elif (self.mi_ccd.temp <= self.mi_ccd.temp_lowlimit):
                #print "amarillo"
                self.temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))
            else :
                self.temp.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
                #print 'rojo'
############################################################################
    def saca_datos_gui(self):
        #sacar los valores del gui
        self.mi_ccd.xorg=int(self.e_xorg.get_text())
        self.mi_ccd.yorg=int(self.e_yorg.get_text())
        self.mi_ccd.xsize=int(self.e_xsize.get_text())
        self.mi_ccd.ysize=int(self.e_ysize.get_text())

        self.mi_ccd.etime=float(self.e_tiempo.get_text())
        #self.mi_ccd.n_frames=int(self.e_frames.get_text())
        self.object = self.objetoid.get_text()
        self.fit_coment = self.comentario.get_text()
        #self.instrument = self.e_instrument.get_text()

        self.mi_ccd.revisa_valores()
############################################################################
    def on_b_2pdf_clicked(self, widget, data=None):
        print "converting log to pdf"
        dir = "/imagenes/bitacora"
        utime = time.strftime("%Y_%m_%d", time.gmtime(None))
        file = "mez_bitacora_"+utime+".csv"
        logfile = os.path.join(dir,file)
        print logfile
        if not  os.path.exists(logfile):
            print "no existe la bitacora"
            self.mi_ccd.mis_variables.mensajes('User Log File not Found! '+logfile,LOG,'red')
            self.mi_ccd.mis_variables.mensajes('You may generate it manualy at :',LOG,'yellow')
            self.mi_ccd.mis_variables.mensajes(dir,LOG,'yellow')
            self.mi_ccd.mis_variables.mensajes('Using the command: csv2pdf.py bitacora_YY_MM_DD.csv',LOG,'yellow')
            return
        else:
            self.mi_ccd.mis_variables.mensajes('Procesing Logfile '+logfile,LOG,Color='blue')

        #ejecutar mando externo
        util=c_util.UTIL()
        mando="./libs/csv2pdf.py "+logfile
        print mando
        resp=util.ejecuta(mando)
        self.mi_ccd.mis_variables.mensajes(resp,LOG,)
        print resp

        #salida
        file = "mez_bitacora_"+utime+".pdf"
        outfile = os.path.join(dir,file)

        ##### nuevo, poner copia del pdf en el directorio de trabajo
        dir = self.directorio.get_text()
        #anexar path defaul imagenes
        dir = os.path.join('/imagenes/',dir,file)
        try:
            copy2(outfile,dir)
        except:
            print "Unable to copy your log file to the working directory"
        #####

        pid=os.spawnlp(os.P_NOWAIT, "/usr/bin/okular", "okular", outfile)
        util.kill_pid_list(pid)

        print "Ya sali"
############################################################################
    def on_b_restart_clicked(self, widget, data=None):
        self.mi_ccd.mis_variables.mensajes("Restart Iraf & Ds9",LOG)

        #elimnar iraf y ds9
        #hacer thread
        thread = threading.Thread(target=self.ds9.restart_iraf_ds9)
        thread.start()
        os.system('./restart_iraf.sh')
############################################################################
    def on_b_roi2center_clicked(self, widget, data=None):
        print "roi to center"
        pangulo=float(self.e_posl.get_text())
        print "Angulo de platina:",pangulo
        gra_rad=math.pi/180.0

        cx,cy,w,h,angulo=self.ds9.roi(1)
        m="Traje de Ds9 box=%d,%d,%d,%d"%(cx,cy,w,h)
        self.mi_ccd.mis_variables.mensajes(m,LOG)
        if w <1:
            self.show_error("Roi Error, Choose a Roi Box in Ds9!")
            return

        #calcular centroide en imagen
        #self.Roi_centroide(cx,cy,w,h)



        #calcular los deltas al centro
        deltax=(self.mi_ccd.xsize_total/2)/self.mi_ccd.cbin-cx
        deltay=(self.mi_ccd.ysize_total/2)/self.mi_ccd.rbin-cy

        print "hola 2, en Roi to Center"
        if self.rotate_axis:
            print "EJE ROTADO"
            x = deltax
            deltax = deltay
            deltay = x

        m="Delta en pixeles, x=%2.2f, y=%2.2f"%(deltax,deltay)
        self.mi_ccd.mis_variables.mensajes(m,LOG)
        m="Escala de placa, dec=%2.3f, ar=%2.3f"%(self.mi_ccd.decscale,self.mi_ccd.arscale)
        self.mi_ccd.mis_variables.mensajes(m,LOG)

        #offdec=deltax*self.mi_ccd.decscale*self.mi_ccd.cbin
        offx=deltax*self.mi_ccd.decscale*self.mi_ccd.cbin*-1

        #offar=deltay*self.mi_ccd.arscale*self.mi_ccd.rbin
        offy=deltay*self.mi_ccd.arscale*self.mi_ccd.rbin*-1

        offdec=offx*math.cos(pangulo*gra_rad)+offy*math.sin(pangulo*gra_rad)
        offar=offy*math.cos(pangulo*gra_rad)-offx*math.sin(pangulo*gra_rad)



        #print offdec,offar


        print offdec,offar

        #calcular por el coseno de dec ar
        self.mi_ccd.mi_telescopio.lee_coordenadas()
        dec=self.mi_ccd.mi_telescopio.dec_dec
        #esta en segundos de tiempo
        offar=(offar/math.cos(dec*gra_rad))/15.0
        #offar=0

        #ahora a compensar con el anglo de platina

        m="Moviendo telescopio offset, Dec=%2.1f, Ar=%2.1f"%(offdec,offar)
        self.mi_ccd.mis_variables.mensajes(m,LOG)


        self.mueve_tel_smart(offdec,offar)



        self.mi_ccd.mis_variables.mensajes('***** Roi to Center Done!!! *****',LOG,Color='green')
    ############################################################################
    def on_b_roi2roi_clicked(self, widget, data=None):
        print "roi to roi"
        pangulo=float(self.e_posl.get_text())   #rotator angle
        print "Angulo de platina:",pangulo
        gra_rad=math.pi/180.0

        #roi1
        cx,cy,w,h,angulo=self.ds9.roi(1)
        m="Traje de Ds9 box=%d,%d,%d,%d"%(cx,cy,w,h)
        self.mi_ccd.mis_variables.mensajes(m,LOG)
        if w <1:
            self.show_error("Roi Error, Choose a Roi Box in Ds9!")
            return

        cx2,cy2,w2,h2,angulo2=self.ds9.roi(2)
        m="Traje de Ds9 box2=%d,%d,%d,%d"%(cx2,cy2,w2,h2)
        self.mi_ccd.mis_variables.mensajes(m,LOG)
        if w <1:
            self.show_error("Roi Error, Choose Two Roi Box in Ds9!")
            return


        #calcular los deltas
        deltax=cx2-cx
        deltay=cy2-cy

        if self.rotate_axis:
            print "EJE ROTADO"
            x=deltax
            deltax=deltay
            deltay=x

        m="Delta en pixeles, x=%2.2f, y=%2.2f"%(deltax,deltay)
        self.mi_ccd.mis_variables.mensajes(m,LOG)
        m="Escala de placa, dec=%2.3f, ar=%2.3f"%(self.mi_ccd.decscale,self.mi_ccd.arscale)
        self.mi_ccd.mis_variables.mensajes(m,LOG)

        #offdec=deltax*self.mi_ccd.decscale*self.mi_ccd.cbin
        #offar=deltay*self.mi_ccd.arscale*self.mi_ccd.rbin

        offx=deltax*self.mi_ccd.decscale*self.mi_ccd.cbin*-1

        #offar=deltay*self.mi_ccd.arscale*self.mi_ccd.rbin
        offy=deltay*self.mi_ccd.arscale*self.mi_ccd.rbin*-1

        offdec=offx*math.cos(pangulo*gra_rad)+offy*math.sin(pangulo*gra_rad)
        offar=offy*math.cos(pangulo*gra_rad)-offx*math.sin(pangulo*gra_rad)


        print offdec,offar


        print offdec,offar
        #calcular por el coseno de dec ar
        self.mi_ccd.mi_telescopio.lee_coordenadas()
        dec=self.mi_ccd.mi_telescopio.dec_dec
        offar=(offar/math.cos(dec*gra_rad))/15.0
        m="Moviendo telescopio offset, Dec=%2.1f, Ar=%2.1f"%(offdec,offar)
        self.mi_ccd.mis_variables.mensajes(m,LOG)

        self.mueve_tel_smart(offdec,offar)

        self.mi_ccd.mis_variables.mensajes('***** Roi 1 to Roi 2 Done!!! *****',LOG,Color='green')
    ############################################################################
    def on_b_restart_clicked(self, widget, data=None):
        self.mi_ccd.mis_variables.mensajes("Restart Iraf & Ds9",LOG)

        #elimnar iraf y ds9
        #hacer thread
        thread = threading.Thread(target=self.ds9.restart_iraf_ds9)
        thread.start()
############################################################################
############################################################################
    def on_full_frame_clicked(self, widget, data=None):
        self.mi_ccd.full_frame()
        #actualizar valores en gui
        self.update_ccd_gui()
    ############################################################################
    def on_ds9roi_clicked(self, widget, data=None):
        '''
        #verificar si  puede el CCD con ROI
        if not self.mi_ccd.bin_n_roi and self.mi_ccd.bin>1:
            m= "No se puede hacer ROI Con Este CCD y con Este Binning"
            print m
            self.mi_ccd.mis_variables.mensajes(m,'nolog','amarillo')

        '''
        print "traer roi"


        cx,cy,w,h,angulo=self.ds9.roi(1)
        self.mi_ccd.xsize=int(round(w))
        self.mi_ccd.ysize=int(round(h))
        self.mi_ccd.xorg=int(round( cx-(w/2) ))
        self.mi_ccd.yorg=int(round( cy-(h/2) ))

        #verificar datos
        self.mi_ccd.revisa_valores()
        #actualizar valores en gui
        self.update_ccd_gui()
############################################################################
    def on_itype_group_changed(self, widget, data=None ):
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        print "image type changed ",data
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])



        activo=widget.get_active()
        print "activo",activo
        if activo:
            self.imgtype=data

############################################################################
    #procesa mensajes de queue
    def procesaMensaje(self):
        if not self.queue.empty():
            #print "llego dato queue..."
            data = self.queue.get()
            #if DEBUG: print "Queue value: ",data

            data = data.split()
            if data[0] == "DO_EXPONE":
                self.on_expone_clicked(data[1],int(data[2]))
            elif data[0] == "EXPON":
                self.on_expone_clicked('none',2)

            elif data[0] == "RUCA_DONE":
                self.e_filtros.set_text(self.mi_ccd.mi_filtro.filtro)
                self.e_filtros.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))

            elif data[0] == "RUCA_UPDATE":
                self.e_filtros.set_text(self.mi_ccd.mi_filtro.filtro)
            elif data[0] == "MEXMAN_UPDATE":
                self.e_filtros.set_text(self.mi_ccd.mi_filtro.filtro)
                self.e_filtros.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
            elif data[0] == "GUI_UPDATE":
                while gtk.events_pending(): gtk.main_iteration()
            elif data[0] == "UPDATE_BARRA":
                max = len(data)-1
                progreso = float(data[max])
                if data[1] == "TIME":
                    texto = string.join(data[2:max])
                elif data[1] == "READING":
                    texto = string.join(data[1:max])
                elif data[1] == "done.":
                    texto = "Done!!!"
                else:
                    texto = string.join(data[1:max])
                if (progreso > 0):
                    progreso/=100.0
                    if progreso <= 1.0:
                        self.barra.set_fraction(progreso)
                        self.barra.set_text(texto)
            elif data[0] == "COLOR_BARRA":
                self.barra.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(data[1]))
            elif data[0] == "UPDATE_TEMP":
                self.temp.set_label(string.join(data[1:]))
            elif data[0] == "MENSAJE":
                self.mensajes(data)
            elif data[0] == "LOGGIN_DEBUG":
                log = string.join(data[1:])
                #logging.debug(log)

            elif data[0] == "FLI_BPOWER":
                self.e_fli_bpower.set_text(string.join(data[1:]))
            elif data[0] == "SBIG_BPOWER":
                self.e_sbig_bpower.set_text(string.join(data[1:]))
            elif data[0] == "SHOW_ERROR":
                self.show_error(string.join(data[1:]))
            elif data[0] == "UPDATE_POL2":
                #polima2
                self.polima2_angulo.set_text(str(self.mi_ccd.mi_filtro.angulo))
                while gtk.events_pending(): gtk.main_iteration()

        return True
############################################################################
    #mensajes(self,msg,tipo="None",Color="None"):
    def mensajes(self, data):
        l=len(data)-1
        msg = string.join(data[1:l-1])
        tipo = data[l-1]
        Color = data[l]
        if Color=="None":
            tag=self.Tag
        elif Color=='rojo' or Color=='red':
            tag=self.Tag_rojo
        elif Color=='verde'or Color=='green':
            tag=self.Tag_verde
        elif Color=='blue' or Color=='azul':
            tag=self.Tag_azul
        elif Color=='amarillo' or 'yellow':
            tag=self.Tag_amarillo
        else:
            tag=self.Tag
            print "Color no definido"
        '''
            print "msg=",msg
        print "tipo=",tipo
        print "color=",Color
        '''

        #print "-------------------------------"
        self.tbuffer.insert_with_tags(self.tbuffer.get_end_iter(), msg+'\n', tag)
        #print "-------------------------------"

        #mover el curso al al final
        iter=self.tbuffer.get_end_iter()
        self.texto.scroll_to_iter(iter,0.0)
        while gtk.events_pending(): gtk.main_iteration()
        #if tipo=="Log":
            #logging.debug(msg)
            #print "no log yet"
############################################################################
    def on_b_open_clicked(self, widget, data=None ):
        print 'open shutter'
        self.abre_shutter()
############################################################################
    def on_b_close_clicked(self, widget, data=None ):
        print 'close shutter'
        self.cierra_shutter()
############################################################################
    def on_b_close_seq_clicked(self, widget, data=None ):
        print 'close sequiencia'
        self.frame_sec.hide()
        #falta hacer chica la ventana
############################################################################
    def on_b_stop_sec_clicked(self, widget, data=None ):
        print '\n\n******************* CANCEL secuence **********************\n\n'
        self.STOP_secuencia=True
        while gtk.events_pending(): gtk.main_iteration()
        self.on_cancela_clicked(None,None)
        while gtk.events_pending(): gtk.main_iteration()
        print '\n******************* Stop ended ********************** \n'
############################################################################
    def on_b_exec_sec_clicked(self, widget, data=None ):
        print 'executa sequencia'
        self.mi_ccd.stop=False
        self.stop = False
        self.mi_ccd.ccd_ready=True
        self.is_exec_macro=True
        self.estadoBotones(False)
        self.STOP_secuencia=False
        oldtime=self.mi_ccd.etime

        s=self.shutter_mode #respaldar modo inicial

        nombre=self.macros.lista_nombres[self.c_secuencias.get_active()]
        print "Vamos a ejecutar macro",nombre
        self.modo_mez=nombre
        pasos=self.macros.dict_lista[nombre]
        l=len(pasos)
        print "con %d instrucciones"%l
        self.mi_ccd.mis_variables.mensajes('Ejecutanto Macro: '+nombre,'nolog','verde')

        conta=0
        for p in pasos:
            conta+=1
            if self.STOP_secuencia:
                print 'Cancelando Secuenecias'
                break
            t='%s \t\t          (paso %d de %d)'%(p,conta,l)
            self.mi_ccd.mis_variables.mensajes(t,'nolog','azul')
            self.e_step.set_text(p)

            ## subrayar linea de macro utilizada
            iter_ini=self.tbuffer2.get_iter_at_line(conta)
            iter_fin=self.tbuffer2.get_iter_at_line(conta+1)
            self.tbuffer2.apply_tag(self.Tag_azul2,iter_ini,iter_fin)
            #mover el curso al al final
            #iter=self.tbuffer.get_end_iter()
            self.texto2.scroll_to_iter(iter_fin,0.0)

            ##
            while gtk.events_pending(): gtk.main_iteration()
            if self.stop: break
            if self.mi_ccd.stop: break
            self.analizaMacro(p)
            #Quitar lo subrayado
            self.tbuffer2.remove_tag(self.Tag_azul2,iter_ini,iter_fin)

        self.e_step.set_text('Done..!')
        self.estadoBotones(True)

        #V2.13 poner modo object otra vez
        self.mi_ccd.etime =oldtime
        self.imgtype='object'

        #if s=='Remote':
        #forzar a siempre remoto
        print 'vamos a devolver el modo a remote'
        self.c_shutter.set_active(0)
        self.deshabilita_shutter()
        self.is_exec_macro = False


        self.mi_ccd.mis_variables.mensajes('===> Macro: '+nombre+' DONE!! <===','nolog','verde')

############################################################################
    def on_b_load_sec_clicked(self, widget, data=None ):
        print 'load sequencia'
############################################################################
############################################################################
    def analizaMacro(self,linea):
        #macros

        print "AnalizaMacro Ejecutando instruccion ",linea
        if len(linea)<1: return
        ln = linea.strip()
        arg = ln.split()
        if arg[0]== '#':
            self.mi_ccd.mis_variables.mensajes("[coment]: "+linea)
        elif arg[0] == "expon":
            if self.mi_ccd.etime >0:
                self.imgtype='object'
            else:
                self.imgtype='zero'

            #estara ya esponiendo
            print 'is CCD completed:',self.is_ccd_completed

            if self.is_ccd_completed==False:
                self.mi_ccd.mis_variables.mensajes("Hey, the CCD is already taking a selfie, wait..")

            while not self.is_ccd_completed:
                if self.STOP_secuencia: break
                if self.stop: break
                self.delay_gui_safe(1)

            print 'CCD is Ready, next exposure will continue'
            if not self.mi_ccd.stop:
                #Hacerlo multitarea
                ethread = threading.Thread(target=self.on_expone_clicked,args = (None,2,'MEZ'))
                ethread.start()
            #self.on_expone_clicked(None,2)
        elif arg[0] == "wait_ccd":
            #espera a que termine el ccd
            while not self.is_ccd_completed:
                if self.STOP_secuencia: break
                if self.stop: break
                self.delay_gui_safe(1)

        elif arg[0] == "tint":
            #argumento da milisegundos
            self.mi_ccd.etime = float(arg[1])/1000.0
            self.update_ccd_gui()
        elif arg[0] == "delay":
            #argumento da milisegundos
            s= int(arg[1])/1000
            print 'delay',s
            self.delay_gui_safe(s,True)
        elif arg[0] == "slit":
            #numeros
            print 'slit'
            n= int(arg[1])
            self.cambia_slit(n)
        elif arg[0] == "mirror":
            print 'mirror'
            #elf.f_mirror.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
            #elf.is_moving+=1
            if arg[1]=='in':
                print "do_mirror in"
                #elf.espejo_in()
                #elf.espera_mirror(1)
                self.r_mirror_in.set_active(True)
            else:
                print "do_mirror out"
                #elf.espejo_out()
                #elf.espera_mirror(0)
                self.r_mirror_out.set_active(True)
            #elf.f_mirror.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
            #elf.is_moving-=1

        elif arg[0] == "shutter":
            #open close
            print 'shutter',arg[1]
            if arg[1]=='open':
                self.abre_shutter()
            else:
                self.cierra_shutter()

        elif arg[0] == "diffuser":
            #in out
            print 'diffuser'
            #elf.f_diffuser.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
            #elf.is_moving+=1
            if arg[1]=='in':
                print "difusser in"
                #elf.difusor_in()
                self.r_diffuser_in.set_active(True)
                #elf.espera_difusor(1)
            else:
                print "diffuser out"
                #elf.difusor_out()
                self.r_diffuser_out.set_active(True)
                #elf.espera_difusor(0)
            #elf.is_moving-=1
            #elf.f_diffuser.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        elif arg[0] == "lamp":
            #arc off tun
            print 'lamp'
            index=arg[1]
            if index=='off':
                print 'apagar lampara'
                self.apaga()
            elif index=='tun':
                print "enciende Tungsten"
                self.enciende(1)
            elif index=='arc':
                print "enciende Th-Ar"
                self.enciende(0)

        elif arg[0] == "posmot":
            print 'posmot'
            self.espera_motores_mezcal()

        elif arg[0] == "move_tel":
            a=float(arg[1])
            d=float(arg[2])

            gra_rad=math.pi/180.0
            self.mi_ccd.mi_telescopio.lee_coordenadas()
            dec=self.mi_ccd.mi_telescopio.dec_dec
            offar=(a/math.cos(dec*gra_rad))/15.0

            self.mueve_tel_smart(d,offar)

        elif arg[0] == "guider_on":
            self.move_guider_enable.set_active(1)

        elif arg[0] == "guider_off":
            self.move_guider_enable.set_active(0)
            if self.is_auto_guiding:
                print "Ya estas guiando, vamos a cancelar"
                self.mis_variables.mensajes("*** Cancelando Guiado ***",Color="amarillo")
                self.is_auto_guiding=False
                self.guiador.CAM.aborta_guiado()





        time.sleep(1)
############################################################################
    def mueve_tel_DOS(self,x,y):
        print "Mueve tel Rutina Mezcal",x," ",y

        if x>=0: fx = 1
        else: fx = -1
        if y>=0: fy = 1
        else: fy = -1

        ciclosx = int(abs(x)/99)
        ciclosy = int(abs(y)/99)
        print "ciclos x ",ciclosx
        print "ciclos y",ciclosy
        if ciclosx >= ciclosy: ciclos = ciclosx
        else: ciclos = ciclosy

        for i in range(0,ciclos):
            print '***** entrando a ciclos *****'
            if i < ciclosx:
                mandax = 99*fx
                self.mi_ccd.mi_telescopio.dec_offset(mandax)
                x -= 99*fx

                time.sleep(2)
            if i< ciclosy:
                manday = 99*fy
                self.mi_ccd.mi_telescopio.ar_offset(manday)
                y -= 99*fy

                time.sleep(2)
        mandax = x
        datoredx = "DEC_OF %6.2f " %(mandax)
        print datoredx
        self.mi_ccd.mi_telescopio.dec_offset(mandax)

        time.sleep(2)
        manday = y
        datoredy = "AR_OF %6.2f "%(manday)
        print datoredy

        self.mi_ccd.mi_telescopio.ar_offset(manday)
############################################################################
    def mueve_tel_smart(self,offdec,offar):
        print 'en mueve tel smart'

        check=self.move_guider_enable.get_active()
        auto=self.is_auto_guiding

        if auto:
            print "Apagando Guiado"
            self.guiador.CAM.aborta_guiado()


        self.mueve_tel_DOS(offdec,offar)

        #guiador
        if check==True:
            self.mi_ccd.mis_variables.mensajes('Vamos a mover Guiador',LOG)
            dec=self.mi_ccd.mi_telescopio.dec_dec
            gra_rad=math.pi/180.0
            self.mueve_guiador(offdec,offar*15.0*math.cos(dec*gra_rad))

        if auto:
            print "Re_activando Guiado"
            #x=self.caja_x*4
            #y=self.caja_y*4

            x=self.caja_x
            y=self.caja_y
            time.sleep(10)
            self.guiador.CAM.activa_guiado(x,y)

        print 'mueve tel smart DONE!'
############################################################################
    def show_error(self, error_string):
        """This Function is used to show an error dialog when
        an error occurs.
        error_string - The error string that will be displayed
        on the dialog.
        """
        error_dlg = gtk.MessageDialog(parent=self.main_window,type=gtk.MESSAGE_ERROR
                                , message_format=error_string
                                , buttons=gtk.BUTTONS_OK)
        response=error_dlg.run()
        error_dlg.destroy()
############################################################################
    def upgrade_fits_mezcal(self):

        outfile=self.outfile
        print 'upgrade_fits_mezcal ',outfile


        hdufile = pyfits.open(outfile, mode='update')
        hdr = hdufile[0].header
        image_data = hdufile[0].data


        #del ccd
        hdr.set("GAIN", self.mi_ccd.gain,"Electrons per ADU")
        #hdr.set("READNOIS", self.mi_ccd.read_noise,"Readout Noise in electron per pixel")

        hdr.set("FILTER", self.lista_filtros[self.filtro],"Filter")
        hdr.set("WHEEL",self.lista_wheel[self.wheel],"Wheel",after='FILTER')

        hdr.set("GRATING",self.rejilla_mes, "Grating",after='FILTER')
        hdr.set("APERTURE",self.lista_rendijas[self.slit], "Aperture",after='FILTER')
        hdr.set("MIRROR",self.lista_carro_pos[self.mirror], "Mirror",after='FILTER')
        hdr.set("DIFFUSER",self.lista_carro_pos[self.diffuser], "diffuser",after='FILTER')

        hdr.set("LAMP",self.lamp_txt, "lamp",after='FILTER')
        #hdr.set("LAMPSTAT",self.estado_lamp, "lamp state",after='FILTER')

        hdr.set("FLOCK",self.seguro_foco, "Focus Lock state,1=lock, 0=unlock",after='FILTER')
        hdr.set("SHUTTER",self.shutter_mode, "shutter mode",after='FILTER')

        hdr.set("MEZMODE",self.modo_mez, "Macro name or image",after='FILTER')


        #self.posa=self.e_posa.get_text()
        self.posl=self.e_posl.get_text()
        #hdr.set("PA",self.posa, "Mes Position Angle ",after='FILTER')
        hdr.set("PL",self.platina.angulo, "Rotator Angle",after='FILTER')
        hdr.set("PA", self.e_ppa.get_text(), "PA Angle", after='FILTER')

        hdr.set("SCALEPIX",self.plate_scale, "arcsec/pixel in spatial direction at BIN 1",after='FILTER')
        #hdr.update("PSCALE",a, "arcsec/pixel in spatial direction",after='FILTER')
        #hdr.update("PIXSCAL1",self.plate_scale, "arcsec/pixel in spatial direction",after='FILTER')
        #hdr.update("PIXSCAL2",self.plate_scale, "arcsec/pixel in spatial direction",after='FILTER')
        #hdr.update('BZERO', 32768, 'BZERO')
        #hdr.update('BSCALE', 1, 'BSCALE')

        '''
        key=hdr.ascardlist()['BITPIX']
        print key

        n=image_data
        print "=========================="
        print "dim",n.ndim
        print "shape",n.shape
        print "type",n.dtype
        print "itemsize",n.itemsize
        print "=========================="
        '''


        #hdufile.scale('int16',bzero=32768)
        hdufile.close()


        #arreglar bu de 32 bits a 16
        #/home/observa/Colorado/mypython
        cmd='/home/observa/Colorado/mypython/fix16.sh %s'%self.outfile
        print cmd
        #os.system(cmd)

        self.ds9.loadfile(self.outfile)
        print 'mezcal header upgraded ENDED'

############################################################################
    def on_b_debug_clicked(self, widget, data=None ):
        print 'debug'
        self.update_pos_mezcal()
        self.mezcal_info()
        #usar eventbox
        #self.ee_wheel.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        #self.ee_wheel.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))

        #pruebas
        iter=self.tbuffer2.get_iter_at_line(3)
        iter2=self.tbuffer2.get_iter_at_line(4)
        self.tbuffer2.apply_tag(self.Tag_azul2,iter,iter2)
        #self.tbuffer2.insert_with_tags(iter, 'hola \n',self.Tag_azul2)

        print 'guador auto=',self.move_guider_enable.get_active()
############################################################################
    def delay_gui_safe(self,segundos=1,p=False):
        if p: print 'delay_gui_safe',segundos,'segundos'
        if p: self.mi_ccd.mis_variables.mensajes('Waiting %d seconds to continue.....'%(segundos),LOG,'blue')

        #2023
        offset=0
        if self.is_ccd_completed == False:
            #es una exposicion
            offset=10
        t_now=t_ini=time.time()
        #esperar con ciclos de un f/segundo actualizanfo la gui
        for s in range(0,segundos*10):
            if self.stop:
                    print 'delay gui cancelado'
                    return
            #print 'en delay gui safe ',s, ' de ',segundos, ' 10/segundos'
            time.sleep(0.1)
            t_now=time.time()
            if t_now-t_ini >(segundos+offset):
                print 'Ya paso el tiempo de espera '
                break
            while gtk.events_pending(): gtk.main_iteration()
        print 'realmente tarde =',t_now - t_ini
        if p: self.mi_ccd.mis_variables.mensajes('OK to continue.....',LOG,'blue')
############################################################################
    def espera_motores_mezcal(self):
        print 'en espera motores mezcal'


        ok=True
        conta=0
        while ok:
            self.delay_gui_safe(1)
            conta+=1
            if conta >10: break
            print 'is moving=',self.is_moving
            if self.is_moving==0:
                print "No se mueve nada de mezcal"
                ok=False
############################################################################
    def userlog(self):
        print '***** user log ****'
        dir = "/imagenes/bitacora"
        utime = time.strftime("%Y_%m_%d", time.gmtime(None))
        file = "mez_bitacora_"+utime+".log"
        logfile = os.path.join(dir,file)

        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(logfile):
            #crea archivo y guarda header
            log = open(logfile, "a+")
            header  = "Fecha: %s\t\tTelescopio: %s \t Observadores: %s\n"%(utime,self.tel,self.observerb2f)
            header += "Instrumento: %s\tDetector: %s %s \n" %(self.instrument,self.mi_ccd.tipo,self.mi_ccd.label2)
            header += "Imagen\t\tObjeto\t\tModo MES\tPL Rendija\tFoco_Tel\tXtemp\tIncl Rejilla\tFiltro\t T.U\t    T.S\t\tt_exp.\tComentarios\n"
            header += "---------------------------------------------------------------------------------------------------------------------------\n"
            log.write(header)
            log.close()

        # por bug, forzar bias en cero
        #checar que bias siempre tenga t=0
        '''
        if self.imgtype=='zero':
            print "es BIAS"
            etime=0
        else:
            etime=self.mi_ccd.etime
        '''
        etime = float(self.e_tiempo.get_text())

        #guarda contenido
        log = open(logfile, "a+")
        data  = self.ultima_imagen.get_text()+"\t"+self.object+"\t\t"+str(self.mi_ccd.mi_telescopio.ar)+"\t"+str(self.mi_ccd.mi_telescopio.dec)+"\t"+str(self.mi_ccd.epoca)+"\t"
        data += str(self.mi_ccd.cbin)+"x"+str(self.mi_ccd.rbin)+"\t"+self.mi_ccd.mi_filtro.filtro+"\t"+str(self.mi_ccd.mi_secundario.foco)+"\t   "+str(self.mi_ccd.airmass)+"\t  "
        data += self.mi_ccd.ut+"  "+self.mi_ccd.ts+"\t"+str(etime)+"\t"+self.fit_coment+"\t"+str(self.mi_ccd.xtemp)+"\n"
        log.write(data)
        log.close()

        #ahora hacer lo mismo pero con formato compatible para csv y exel
        file = "mez_bitacora_"+utime+".csv"
        logfile = os.path.join(dir,file)
        if DEBUG: print "cvs",logfile
        #existe el archivo ?
        do_header=not os.path.exists(logfile)
        log = open(logfile, "ab+")
        csv.register_dialect('bitacora', dialect='excel',delimiter=',', quoting=csv.QUOTE_NONE)
        writer = csv.writer(log,'bitacora')


        #header
        if do_header:
            print 'No hay header de csv'
            #crea archivo y guarda header
            a="Fecha: %s\tTelescopio: %s \t Observadores: %s"%(utime,self.tel,self.observerb2f)
            print a
            header  = [a]
            if DEBUG: print header
            writer.writerow(header)
            a="Instrumento: %s\tDetector: %s %s " %(self.instrument,self.mi_ccd.tipo,self.mi_ccd.label2)
            header  = [a]
            print header
            writer.writerow(header)
            header = ["Imagen","Objeto","Modo","PL. Rendija","Rendija","Foco_Tel","xTemp","Incl Rejilla","Filtro"," T.U","T.S","tt_exp.","Comentarios"]
            if DEBUG: print header
            writer.writerow(header)
            header = ["---------------------------------------------------------------------------------------------------------------------------"]

            writer.writerow(header)



        #datos
        data  = [self.ultima_imagen.get_text(),self.object,self.modo_mez,self.e_posl.get_text(),self.lista_rendijas[self.slit]]
        data += [str(self.mi_ccd.mi_secundario.foco),str(self.mi_ccd.xtemp),self.e_gratin.get_text(),self.lista_filtros[self.filtro]]
        data += [self.mi_ccd.ut,self.mi_ccd.ts,str(etime),self.fit_coment]


        #if DEBUG: print "cvs data=",data
        writer.writerow(data)
        #cerrar
        log.close()
############################################################################
    def post_expone(self):
        if DEBUG: print "post expone init........"
        self.mi_ccd.mis_variables.update_barraColor('green')
        self.mi_ccd.mis_variables.update_barra("done. ",0.001)

        self.mi_ccd.mi_filtro.postexpone(self.mi_ccd)


        self.mi_ccd.post_expone(self.outfile)
        ##############################
        #print 'do dark subs',self.mi_ccd.do_dark_subs


        #############################
        #self.userlog()

        try:
            self.userlog()
        except:
            print "NO PUDE HACER EL LOG ->userlog"

        print '\a'
        os.system('beep')

        #self.checa_temp()
        self.backup_oan()

############################################################################
    def on_c_secuencias_changed(self, widget, data=None ):
        print 'secuencias cambio'
        nombre=self.macros.lista_nombres[self.c_secuencias.get_active()]
        pasos=self.macros.dict_lista[nombre]

        self.tbuffer2.set_text(nombre+'\n')



        for linea in pasos:
            self.tbuffer2.insert(self.tbuffer2.get_end_iter(),'==> '+linea+"\n")


############################################################################
    def do_default (self):
        print "en do_default ------------------------------"
        #poner defaults para el menu de seleccion inicial
        #usando las variables de ambiente

        #poner telescopio
        #self.t_tel.set_text(self.comm.tel)
        #instrumento
        #if self.params.var['CCD_INSTRUMENT']:
        #    self.e_instrument.set_text(self.params.var['CCD_INSTRUMENT'])
        #observer
        if self.params.var['CCD_OBSERVER']:
            self.observer.set_text(self.params.var['CCD_OBSERVER'])
        #ccd
        if self.params.var['CCD_CCD']:
            self.l_ccdtxt.set_text(self.params.var['CCD_CCD'])
            self.t_ccd.set_text(self.params.var['CCD_CCD'])

        if self.params.var['CCD_BASE']:
            self.basename.set_text(self.params.var['CCD_BASE'])

        if self.params.var['CCD_OBJECT']:
            self.objetoid.set_text(self.params.var['CCD_OBJECT'])

        if self.params.var['CCD_WDIR']:
            self.directorio.set_text(self.params.var['CCD_WDIR'])

        if self.params.var['CCD_LAST']:
            self.ultima_imagen.set_text(self.params.var['CCD_LAST'])

        if self.params.var['CCD_MACRO']:
            #nombre=self.macros.lista_nombres[self.c_secuencias.get_active()]
            try:
                n=self.macros.lista_nombres.index(self.params.var['CCD_MACRO'])
                #print 'el numero de macro usado es',n
                self.c_secuencias.set_active(n)
            except:
                print 'No encontre macro usado'

############################################################################
    def do_load_last_parms(self):
        self.mi_ccd.mis_variables.mensajes("Note: Loading last session parameters...",Color='amarillo')

        if self.params.var['CCD_BINN']:
            a=self.params.var['CCD_BINN']
            a=a.split()
            if DEBUG:
                print "traje bin de params",a
            try :
                cols=int(a[0])
            except:
                cols=1

            try :
                rows=int(a[1])
            except:
                rows=1

        self.xbin.set_active(cols-1)
        while gtk.events_pending(): gtk.main_iteration()

        self.ybin.set_active(rows-1)
        while gtk.events_pending(): gtk.main_iteration()

        if self.params.var['CCD_XORG']:
            self.e_xorg.set_text(self.params.var['CCD_XORG'])

        if self.params.var['CCD_YORG']:
            self.e_yorg.set_text(self.params.var['CCD_YORG'])

        if self.params.var['CCD_XSIZE']:
            self.e_xsize.set_text(self.params.var['CCD_XSIZE'])

        if self.params.var['CCD_YSIZE']:
            self.e_ysize.set_text(self.params.var['CCD_YSIZE'])

        self.saca_datos_gui()
############################################################################
    def on_b_gcenter_clicked(self, widget, data=None ):
        #no la uso
        print 'centro guiador'
        self.guiador.estado()
        self.guiador.info()
        self.guiador.trae_imagen()
        Cx,Cy=self.guiador.centroide()
        t="Guiador: AR=%3.2f, DEC=%3.2f, Cx=%3.2f, Cy=%3.2f"%(self.guiador.ar,self.guiador.dec,Cx,Cy)
        print t
        self.mi_ccd.mis_variables.mensajes(t,'nolog','azul')

############################################################################
    def on_b_guide_clicked(self, widget, data=None ):
        print 'star guiding'
############################################################################
    def on_b_load_sec_clicked(self, widget, data=None ):
        print 'carga tus secuencias'
        ok=False
        dialog = gtk.FileChooserDialog("Open your Mezcal Sequence file...",
            None, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)


        filter = gtk.FileFilter()
        filter.set_name("Mezcal macro Files (.mezcal)")
        filter.add_pattern("*.mezcal")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        #directorio de trabajo default
        homedir = os.path.expanduser('~')
        dialog.set_current_folder(homedir)
        while True:
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                archivo=dialog.get_filename()
                ext = os.path.splitext(archivo)[1]
                if ext==".mezcal" :
                    print archivo, 'selected'
                    self.macro_file = archivo
                    #self.run_macro.set_sensitive(True)
                    ok=True
                    break
                else:
                    print archivo, 'invalid macro file'
            elif response == gtk.RESPONSE_CANCEL:
                print 'Closed, no files selected'
                break
        dialog.destroy()
        if ok:
            m='Mezcal Macro file loaded -> '+self.macro_file
            self.mi_ccd.mis_variables.mensajes(m,LOG,'azul')
            #recargar nuevos macros
            self.macros.reload_macro(archivo)

            print self.macros.lista_nombres
            del self.c_secuencias
            del self.lseq
            self.c_secuencias = self.builder.get_object("c_secuencias")
            self.lseq=gtk.ListStore(str)


            for d in self.macros.lista_nombres:
                #print d
                self.lseq.append( [d] )

            self.c_secuencias.set_model(self.lseq)   #this replaces the model set by Glade
            cell = gtk.CellRendererText()
            self.c_secuencias.pack_start(cell)
            #self.c_secuencias.add_attribute(cell, 'text', 0)
            #make the first row active
            self.c_secuencias.set_active(0)

############################################################################
    def on_b_load_defaultsec_clicked(self, widget, data=None ):

        self.macro_file=archivo='/usr/local/instrumentacion/Mezcal2014/secuencias.mezcal'
        m='Mezcal Macro file loaded -> '+self.macro_file
        self.mi_ccd.mis_variables.mensajes(m,LOG,'azul')
        #recargar nuevos macros
        self.macros.reload_macro(archivo)

        print self.macros.lista_nombres
        del self.c_secuencias
        del self.lseq
        self.c_secuencias = self.builder.get_object("c_secuencias")
        self.lseq=gtk.ListStore(str)


        for d in self.macros.lista_nombres:
            #print d
            self.lseq.append( [d] )

        self.c_secuencias.set_model(self.lseq)   #this replaces the model set by Glade
        cell = gtk.CellRendererText()
        self.c_secuencias.pack_start(cell)
        #self.c_secuencias.add_attribute(cell, 'text', 0)
        #make the first row active
        self.c_secuencias.set_active(0)
############################################################################
    def backup_oan(self):
        print "*** OAN Backup ***"

        archivo=self.genera_formato_backup(self.tel,self.instrument,self.fechatiempo)
        #print "archivo para db",archivo
        dir='/imagenes/oan_backup'
        fullfile = os.path.join(dir,archivo)

        if not os.path.exists(dir):
            os.makedirs(dir)
        copy2(self.outfile,fullfile)

############################################################################
    def mueve_guiador(self,offdec,offar):
        m="Moving Guider offsets to dec=%3.2f, ar=%3.2f"%(offdec,offar)
        self.mi_ccd.mis_variables.mensajes(m,LOG,Color='blue')
        print m

        #leer pos guiador
        self.guiador.estado()
        self.guiador.info()

        ar=self.guiador.ar-offar
        dec=self.guiador.dec+offdec

        self.guiador.mueve(ar,dec)

############################################################################
    def on_b_show_guider_clicked(self, widget, data=None ):
        if self.guiador_win_is_active:
            self.frame_guiador.hide()
            self.guiador_win_is_active=False
        else:
            self.frame_guiador.show()
            self.guiador_win_is_active=True

############################################################################
    def on_cb_show_sys_toggled(self, widget, data=None):
            print "%s was toggled %s" % ('Show Sys MSG', ("OFF", "ON")[widget.get_active()])
            if widget.get_active():
                self.scrolledwindow.show()
                self.main_window.resize(824,710)
            else:
                self.scrolledwindow.hide()
                #rect = self.main_window.allocation
                #pos=self.main_window.get_position()

                self.main_window.resize(824,509)
############################################################################
############################################################################
    def on_b_auto_clicked(self,widget, data=None ):
        #auto guider
        print "presionastes el boton auto guiador"

        #mandar a guiar con la caja
        x=self.caja_x
        y=self.caja_y

        if self.is_auto_guiding:
            print "Ya estas guiando, vamos a cancelar"
            self.g_auto.set_label("Auto")
            self.g_auto.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
            self.mis_variables.mensajes("*** Cancelando Guiado ***",Color="amarillo")
            self.is_auto_guiding=False
            self.guiador.CAM.aborta_guiado()
        else:
            print "Vamos a Guiar"
            self.g_auto.set_label("Cancel")
            self.g_auto.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
            self.is_auto_guiding=True
            self.mis_variables.mensajes("*** Activando Guiado ***",Color="verde")
            self.move_guider_enable.set_active(1)
            self.guiador.CAM.trae_imagen()
            self.guiador.CAM.activa_guiado(x,y)

############################################################################
    def on_b_gexpone_clicked(self,widget, data=None ):
        print "presionastes el boton expone"
        t=float(self.e_tiempo_guiador.get_text())*1000.0
        print 't=',t

        #exponer bineado
        self.guiador.CAM.expone(t)

        #traer imagen y mostrar
        self.guiador.CAM.trae_imagen_pgm()
        self.g_image.set_from_file('/tmp/img.pgm')

############################################################################
    def on_click(self,box,event):
        print 'presionastes el mouse'
        print event.x,event.y



        pixbuf = gtk.gdk.pixbuf_new_from_file('/tmp/img.pgm') #one way to load a pixbuf
        pixmap,mask=pixbuf.render_pixmap_and_mask()
        cm=pixmap.get_colormap()
        red=cm.alloc_color('red')
        gc=pixmap.new_gc(foreground=red)

        #x=event.x-15/2.0
        #y=event.y-15/2.0

        x=event.x-15
        y=event.y-15/2.0

        #respalder posicion
        self.caja_x=event.x-15/2.0
        self.caja_y=event.y

        print "guardando valores de caja",self.caja_x,self.caja_y

        pixmap.draw_rectangle(gc,False,int(x),int(y),15,15)
        #pixmap.draw_rectangle(gc,False,10,10,60,60)
        self.g_image.set_from_pixmap(pixmap,mask)

############################################################################
    def on_b_save_clicked(self, widget, data=None ):
        print 'salvando imagen'
        print 'auto?',self.auto_save.get_active()
############################################################################
    def on_b_ccd_init_clicked(self, widget, data=None):
        print 'CCD init again'
        self.mi_ccd.inicializa()
        self.update_ccd_gui()
############################################################################
#------------------------------------------------------------------------------
if __name__=="__main__":

    #leer opciones
    arg = string.join(sys.argv[1:])
    print arg
    if arg.find('nomezcal')==0:
        NOMEZCAL=True
    else:
        NOMEZCAL=False
    print "NoMezcal",NOMEZCAL

    DEBUG=True    #para algunos print del main
    VERSION='2.23'
    LOG="nolog"
    colores="/usr/local/instrumentacion/Mezcal2014/./mis_colores.rc"
    gtk.rc_set_default_files(colores)
    gtk.rc_parse(colores)

    app=MEZCAL()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
