#!/usr/bin/env python

import c_filtros
from c_filtros import *
from  c_util import *
from c_cliente import *
#import time
import os.path


###########################################################
class SBIG5W(UTIL,CLIENTE,FILTROS):
    'Manejo de la rueda de Filtros Sbig 5 filters'
    
###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        self.archivo_filtros="filtros_sbig5.cfg"
        self.mis_variables = variables
        self.numero_filtros=5
        self.extension='.cfg'
        self.usuario="sbig_5W"
        self.filtro="no se"	#aqui estan los 2 nombres de los filtros
        self.f1=0
        self.f1_name="?"
        self.ip="localhost"
        self.puerto=9777
        self.set_timeout(40)
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros Sbig 5",self.archivo_filtros
        self.rueda_list=["U", "B","V","R","I"]
        try:
            self.auto_carga_archivo_filtros()
        except:
            print 'No pude cargar archivo de de etiquetas',self.archivo_filtros
        
###########################################################
    def pide_posicion(self):
        if self.debug: print 'Sbig5 pidiendo posicion...'
        data,status=self.manda("get_pos ")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi Sbig5",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def mueve_filtros(self,posicion):
        print "moviendo filtros Sbig5 a posicion ",posicion
        t="posicion %d "% posicion
        #t=tuple(t)
        data,status=self.manda(t)
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def procesa_respuesta(self,data):
        #'MEXMAN POS 1 vacio 16 I3\r\n'
        mando=data.split()
        key=mando[0]
        key2=mando[1]
        if key=="posicion":
            #if self.debug:
	    print "llegaron filtros sbig5.."
	    
	    try:
		self.f1=int(mando[1])
	    except:
		self.f1=0
		print 'No pude leer filtro \n'
	    print 'filtro#',self.f1
            self.f1_name=self.rueda_list[self.f1-1]
	    print 'nombre=',self.f1_name 
	    
            self.filtro=self.f1_name
            if self.debug: print "el filtro es=",self.filtro
            #tupla = ["MEXMAN_UPDATE",self.filtro]
	    txt="MEXMAN_UPDATE "+self.filtro
            self.mis_variables.queue.put(txt)
	    
############################################################################
    def auto_carga_archivo_filtros(self):
        try:
            openfile = open(self.archivo_filtros, 'r')
        except:
            a = "Error autoload can't open " + self.archivo_filtros
            print a
            self.mi_ccd.mis_variables.mensajes(a, "Log", "rojo")
            return

        str = openfile.read()
        openfile.close()
        t = str.split('\n')
        print t
        print len(t)
        self.rueda_list=t



############################################################################
#a=MEXMAN()

#a.pide_posicion()
#x=time.time()
#a.mueve_filtros(1)
#print "tarde seg=",time.time()-x
#a.pide_posicion()