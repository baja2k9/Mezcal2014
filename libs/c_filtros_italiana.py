#!/usr/bin/env python

import c_filtros
from c_filtros import *
from  c_util import *
from c_cliente import *
#import time
import os.path

#V0.1 E.colorado >Abril 2012
#V0.2 E.colorado >Julio 2016, lee por default archivo con las etiquetas
###########################################################
class ITALIANA(UTIL,CLIENTE,FILTROS):
    'Manejo de la rueda de Filtros Italiana'

###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        print "Activating Italiana Class"
        self.archivo_filtros="filtros_italiana.cfg"
        self.mis_variables = variables
        self.numero_filtros=19
        self.extension='.cfg'
        self.usuario="italiana"
        self.filtro="no se"	#aqui estan los 2 nombres de los filtros
        self.f1=0
        self.f1_name="?"
        self.f2=0
        self.f2_name="?"
        self.ip="localhost"
        self.puerto=9706
        self.set_timeout(50)
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros Italiana",self.archivo_filtros

        self.debug=True
        self.rueda1_list=["Vacio", "I-Johnson","R-Johnson","V-Johnson","B-Johnson","U-Johnson","Z-Gunn","I-Gunn","R-Gunn","G-Gunn"]
        self.rueda2_list=["V-Gunn","4900/80A","5045/80A","6603/80A","6643/80A","6683/80A","6723/80A","Pol. HN38","Vacio" ]

        try:
            self.auto_carga_archivo_filtros()
        except:
            print 'No pude cargar archivo de de etiquetas',self.archivo_filtros

###########################################################
    def pide_posicion(self):
        if self.debug: print 'Italiana pidiendo posicion...'
        data,status=self.manda("POS")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi italiana",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def mueve_filtros(self,posicion):
        print "moviendo filtros Italiana a posicion ",posicion
        t="MOV %d "% posicion
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
    def mueve_pol(self,angulo,auto=True):
        print "moviendo polarizador Italiana a angulo ",angulo
        t="POL %d "% angulo
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
        #'ITALIANA POS 2 1 0\r\n'

        mando=data.split()
        key=mando[0]
        if key=='BUSY':
            print "BUSY"
            return
        key2=mando[1]
        if key=="ITALIANA" and key2=="POS":
            if self.debug: print "llegaron filtros Italiana.."
            self.f1=int(mando[2])
            self.f2=int(mando[3])
            self.angulo=int(mando[4])

            if self.debug:
                print self.f1,self.f2
                print self.rueda1_list
                print self.rueda2_list

            self.f1_name=self.rueda1_list[self.f1-1]
            self.f2_name=self.rueda2_list[self.f2-1]

            #estara el polarizador rueda2=8
            if self.f2==8:
                print 'esta puesto el polarizador a',self.angulo
                self.filtro="%s+%s=%d" %(self.f1_name,self.f2_name,self.angulo)
                self.filtro = self.filtro.replace('"','')
            else:
                self.filtro="%s+%s" %(self.f1_name,self.f2_name)
                self.filtro = self.filtro.replace('"','')

            if self.debug: print "el filtro es=",self.filtro
            #tupla = ["MEXMAN_UPDATE",self.filtro]
            txt="MEXMAN_UPDATE "+self.filtro
            if self.debug: print txt
            if self.mis_variables!=None:
                self.mis_variables.queue.put(txt)
############################################################################
    def auto_carga_archivo_filtros(self):
        try:
            openfile = open(self.archivo_filtros, 'r')
        except:
            a= "Error autoload can't open "+self.archivo_filtros
            print a
            self.mi_ccd.mis_variables.mensajes(a,"Log","rojo")
            return

            

        str=openfile.read()
        openfile.close()
        t=str.split('\n')
        print t
        print len(t)
        self.rueda1_list=t[0:10]
        self.rueda2_list=t[10:-1]
        
        print self.rueda1_list
        print self.rueda2_list
############################################################################
#a=ITALIANA(None)

#a.pide_posicion()
#x=time.time()
#a.mueve_filtros(1)
#print "tarde seg=",time.time()-x
#a.pide_posicion()
