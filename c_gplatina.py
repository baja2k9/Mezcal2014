# -*- coding: utf-8 -*-

import c_platina2m

# V0.1 E. Colorado, inicial Jun-2015 ->aqui va lo grafico de platina, para no tener tando en el main
############################################################################
class GPLATINA():

    def __init__(self,builder):
        print 'init gplatina'
        self.platina=c_platina2m.PLATINA2M()
        self.platina.PA2=-0.1
        
        self.e_pmove = builder.get_object("e_pmove")
        self.e_pactual = builder.get_object("e_pactual")
        
############################################################################
    def on_b_pstop_clicked(self, widget, data=None ):
        print 'presionaste stop platina'
############################################################################
    def on_b_pmueve_clicked(self, widget, data=None ):
        print 'presionaste mueve platina'
        print self.e_pmove.get_text()
        print self.e_pactual.get_text()
############################################################################
    def on_b_pinit_clicked(self, widget, data=None ):
        print 'presionaste init platina'
############################################################################

############################################################################

############################################################################

