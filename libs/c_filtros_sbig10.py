#!/usr/bin/env python

import c_filtros_sbig5
from c_filtros_sbig5 import *

#import time
import os.path


###########################################################
class SBIG10W(SBIG5W):
    'Manejo de la rueda de Filtros Sbig 10 filters'

###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        SBIG5W.__init__(self,variables)
        self.archivo_filtros="filtros_sbig10.cfg"
        self.mis_variables = variables
        self.numero_filtros=10
        self.usuario="sbig_10W"
        self.ip="localhost"
        self.puerto=9777
        self.set_timeout(40)
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros Sbig 10",self.archivo_filtros
        self.rueda_list=["Luminancia", "R","G","B","Clear","Ha","Vacio7","Vacio8","Vacio9","Vacio10"]
        try:
            self.auto_carga_archivo_filtros()
        except:
            print 'No pude cargar archivo de de etiquetas', self.archivo_filtros

###########################################################
