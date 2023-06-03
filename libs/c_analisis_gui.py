# -*- coding: utf-8 -*-
import gtk
from c_analisis import *


############################################################################
class ANALISIS_GUI(ANALISIS):
    
    debug = None
############################################################################
    def __init__(self,builder,queue=None):
        print "Analisis gui"
        self.builder=builder
        #self.mis_variables=
        self.queue=queue
        #print 'queue',self.queue
        self.win_tfc= builder.get_object("win_tfc")
        self.win_tfc.connect("delete-event", self.esconde_wintfc)
        self.win_tfc.connect("destroy", self.esconde_wintfc)
        
        self.hide_tfc = builder.get_object("b_hidetfc")
        self.hide_tfc.connect("clicked",self.esconde_wintfc,3)
        
        #self.b_run=  builder.get_object("b_run")
        #self.b_run.connect("clicked",self.on_b_run_clicked,0)
        
        self.c_curva=  builder.get_object("c_curva")
        self.c_lineal=  builder.get_object("c_lineal")
        self.c_mono=  builder.get_object("c_mono")
        self.e_inctime=  builder.get_object("e_inctime")
        
        self.e_nseries=  builder.get_object("e_nseries")
        #self.e_nseries.connect("editing-done",self.celda_editing_done)
        
        self.e_tfinal=  builder.get_object("e_tfinal")
        self.e_area=  builder.get_object("e_area")
        self.e_area.set_text('500:600,500:600')
        
        
        ANALISIS.__init__(self)
        print "Analisis gui ended --------------------------------------------------"
############################################################################
    def esconde_wintfc(self, widget, data=None):
        print "esconde ventana wintfc"
        self.win_tfc.hide()
        return True

############################################################################

############################################################################
    def info(self):
        print 'inc. tiempo',self.e_inctime.get_text()
        print 'N. Series',self.e_nseries.get_text()
        print 'T. Final',self.e_tfinal.get_text()
        print 'Curva ?',self.c_curva.get_active()
        print 'Lineal ?',self.c_lineal.get_active()
        print 'Mono ?',self.c_mono.get_active()
        print 'Area=',self.X1,self.Y1,self.X2,self.Y2
############################################################################
    def celda_editing_done(self, widget, data=None):
        print 'termine de editar ',widget
############################################################################
############################################################################
############################################################################
