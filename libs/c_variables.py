#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import gtk
############################################################################
class VARIABLES:
    "Clase para compartir todas las variables, no importa la inicializacion"
    queue = None
    temp=0
    weather_enable=False
    foco = -1
    debug = None
    def __init__(self):
        pass

############################################################################
    def mensajes(self,msg,tipo="None",Color="None"):
        self.msg_gui("MENSAJE "+msg+" "+str(tipo)+" "+str(Color))
############################################################################
    def update_barra(self,texto,progreso):
        #progreso debe estar entre 0 y 100
        #print "barra=",self.barra
        self.msg_gui("UPDATE_BARRA "+texto+" "+str(progreso))
        self.gui_update()
############################################################################
    def update_barraColor(self, bgColor):
        self.msg_gui("COLOR_BARRA "+bgColor)
############################################################################
    def update_temp(self,temp):
        self.temp=temp
        txt="T= "+str(self.temp)
        self.msg_gui("UPDATE_TEMP "+txt)
############################################################################
    def logging_debug(self,log):
        self.msg_gui("LOGGIN_DEBUG "+log)
############################################################################
    def msg_gui(self,txt):
        #print "msg to gui",txt
        if self.queue:
            self.queue.put(txt)
        else: print "queue no inicializada"
############################################################################
############################################################################
    def gui_update(self):
        self.msg_gui("GUI_UPDATE")

############################################################################
    def update_pol2(self):
        self.msg_gui("UPDATE_POL2")

############################################################################