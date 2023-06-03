#!/usr/bin/env python
#V0.2
###########################################################
class FILTROS:
    'Manejo de Filtros Base'
    
    def __init__(self):
        self.numero_filtros=0
        self.usuario="base"
        self.filtro="No_Filter_wheel"
        self.archivo_filtros = ""
        self.archivo_filtros="filtros.fil"
        self.pattern_name="Ruca Files (.fil)"
        self.angulo=None
        self.debug=False
        self.p_name="All Files (.*)"
        extension='*.*'

###########################################################
    def pide_posicion(self):
        print "implementa en cada clase de filtros"

###########################################################
    def mueve_filtros(self,posicion):
        print "implementa en cada clase de filtros"
###########################################################
    def posicion_pol(self):
        #solo polima
        pass
###########################################################
    def mueve_pol(self,pos):
        #solo polima
        pass
###########################################################
    def preexpone(self):
        pass
###########################################################
    def postexpone(self,mi_ccd=None):
        pass
###########################################################
