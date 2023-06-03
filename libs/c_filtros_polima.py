#!/usr/bin/env python
# -*- coding: utf-8 -*-

from  c_util import *
from c_cliente import *
from c_filtros import *

import time
import os
import os.path
import c_ds9
from c_ds9 import *
#ocupa socket server en aplicacion principal
#V1.0, E. Colorado, Mayo 2010, incial
#V1.1, E. Colorado, Enero 2011, modifique postexpone, ahora ya sabe el bin del ccd
#V1.2, E. Colorado, Junio 2011, ahora lee posicion del circulo de polarizador
#V1.3, E. Colorado, Nov 2011, variables para el macro polima_flat
#V1.4 E. Colorado,  Oct 2013, curculo de polima con xorg yorg
###########################################################
class POLIMA(UTIL,CLIENTE,FILTROS):
    'Manejo de polima filtros y polarizador'

    numero_filtros=4
    extension='*.cfg'
    #archivo_filtros="~/polima.cfg"
    archivo_filtros="polima.cfg"
    p_name="Polima Files (.cfg)"
    usuario="polima"
    filtro="no se"
    filtro_pos=-1
    angulo=-1
    __error=0.300
    puerto_respuestas=9700
    filtro_ready=False
    proceso_gui='wish polarimetro_current.tcl'
    programa_gui='/usr/local/instrumentacion/polarimetro/runpolarimetro_net.tcl &'
    #1.3 variables para el macro polima flat
    pnoche=[135,90,45,0] #secuencia de angulos para la noche
    pdia=[0,45,90,135]   #secuencia de angulos para el dia
    nflat= 5		 #numero de flats por angulo
    #npol=  4
    nmin= 15000		#cuentas minimas permitidas
    nmax= 30000		#cuentas maximas permitidas
    tmax= 45		#tiempo maximo de exposicion
    tmin= 0.8		#tiempo minimo de exposicion
    noptimal=27500	#valor promedio de cuentas deseadas
    
    DEBUG=False


###########################################################
    def __init__(self,variables):
        print "################ POLIMA INIT #################"
        self.ip="192.168.0.141" #grulla
        self.puerto=9799
        self.set_timeout(30)
        self.mis_variables = variables
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros polima",self.archivo_filtros

        homedir = os.path.expanduser('~')
        self.archivo_cfg=os.path.join(homedir,"polima2.cfg")
        print "Archivo de configuracion polima",self.archivo_cfg

        self.x=512*2
        self.y=517*2
        self.r=252*2
        self.pol = c_ds9.DS9()
        self.read_config()
        self.info()
        self.checa_gui_polima()

###########################################################
    def posicion_filtros(self):
        if self.DEBUG: print 'polima pidiendo posicion...'
        data,status=self.manda_sin_respuesta("POSFIL")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        return True
###########################################################
    def mueve_filtros(self,posicion,auto=True):
        if self.DEBUG: print "moviendo filtros Polima a posicion ",posicion
        #determinar si es movimiento por numero de filtro o por nombre
        s=''
        s=str(posicion)
        if s.isdigit():
            if self.DEBUG: print "Moviendo polima por posicion"
            t="NMOVFIL %d "% (posicion)
        else:
            if self.DEBUG: print "Moviendo polima por etiqueta"
            t="MOVFIL "+ posicion

        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        if auto:
            self.espera_filtros()
        return True
###########################################################
#No la ocupo, lo puse en la aplicacion principal
    def procesa_respuesta(self,data):
        if self.DEBUG: print "procesa respuesta polima"
        mando=data.split()
        key=mando[1]
        if key=="POS":
            if self.DEBUG: print "llegaron filtros"
            self.f1=mando[2]
            self.f1_name=mando[3]
            self.f2_name=mando[5]
            filtro="%s %s" %(self.f1_name,self.f2_name)
            if self.DEBUG: print "el filtro es=",filtro



############################################################################
###########################################################
    def espera_filtros(self):
        if self.DEBUG: print "esperando filtros de polima"

        loop=1
        while loop:
            time.sleep(0.8)
            data,status=self.manda_sin_respuesta("READY_FIL ")
            self.mis_variables.gui_update()
            time.sleep(0.1)
            if self.filtro_ready:
                loop=0
            else:
                print "polima todavia no cambia su filtro a posicion"+str(self.filtro) +" ready="+str(self.filtro_ready)

        self.posicion_filtros()
        time.sleep(0.1)
        if self.DEBUG: print "Listo los filtros del polima, "+str(self.filtro_pos)+ " "+self.filtro

###########################################################
    def espera_pol(self,deseado):
        if self.DEBUG: print "esperando pol a",deseado
        a=deseado-self.__error
        b=deseado+self.__error

        print "movi polima a %f con errores posibles %f , %f"%(deseado,a,b)

        loop=1
        while loop:
            time.sleep(0.8)
            data,status=self.manda_sin_respuesta("POSPOL ")
            self.mis_variables.gui_update()
            time.sleep(0.1)
            if self.angulo==deseado: break
            if self.angulo >a and self.angulo<b:
                print "polima llego..."
                loop=0
                break
            else:
                print "polima no ha llegado , actual="+str(self.angulo)

###########################################################
    def mueve_pol(self,angulo,auto=True):
        if self.DEBUG: print "moviendo polarizador a",angulo

        t="MOVPOL %f "% angulo
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1

        if auto:
            self.espera_pol(angulo)
        return True
###########################################################
    def posicion_pol(self):
        if self.DEBUG: print "pidiendo pos pol"
        data,status=self.manda_sin_respuesta("POSPOL")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1

        #self.procesa_respuesta(data)
        return True
###########################################################
    def pide_posicion (self):
    	self.posicion_filtros()
###########################################################
    def info(self):
        print "polima info:"
        print "filtro",self.filtro
        print "posicion filtro",self.filtro_pos
        print "angulo",self.angulo
        print "error polarizador",self.__error
        print "ready?",self.filtro_ready
        a="circle x=%d, y=%d, r=%d" % (self.x,self.y,self.r)
        print a
###########################################################
    def postexpone(self,mi_ccd=None):
		print "postexpone polima2"
		print mi_ccd.cbin, " ",mi_ccd.rbin, " ", mi_ccd.bin
		print mi_ccd.xorg,mi_ccd.yorg
		self.pol.circle(self.x/mi_ccd.cbin-mi_ccd.xorg,self.y/mi_ccd.cbin-mi_ccd.yorg,self.r/mi_ccd.cbin)
        
############################################################################
    def read_config(self):
        a=self.archivo_cfg
        print "leyendo archivo de configuracion:",a
        try:
            openfile = open(a, 'r')
        except:
            print "Error, no pude abrir ",a
            return False

        str=openfile.read()
        openfile.close()
        lineas=str.split('\n')
        print lineas
        for linea in lineas:
            print "prcesando linea=",linea
            l=linea.split('=')
            print "separado",l
            if l[0]=='x':
                self.x=int(l[1])
            elif l[0]=='y':
                self.y=int(l[1])
            elif l[0]=='r':
                self.r=int(l[1])
        '''
        self.tel=t[0]
        self.host_marconi=t[1]
        self.puerto_arranque=int(t[2])
        self.weather_server=t[3]
        self.weather_enable=t[4]
        self.host_ccdphoto=t[5]
        self.host_ccdoan=t[6]
        '''
        return True
############################################################################
    def checa_gui_polima(self):
        print "Verificando su polima esta corriendo"
        r=self.checa_proceso(self.proceso_gui)

        if r>0:
            m="Polima ya esta corriendo con PID= "+str(r)
            print m
            self.mis_variables.mensajes(m,"Log","green")
        else:
            m="Polima NO esta corriendo, lo voy a arrancar .."
            self.mis_variables.mensajes(m,"Log","rojo")
            os.system(self.programa_gui)
            print m
	    #pequeno delay para que termine de cargar
	    time.sleep(2)

############################################################################
    def kill_gui_polima(self):
        print "killing polima esta corriendo"
        r=self.checa_proceso(self.proceso_gui)

        if r>0:
            m="Polima si esta corriendo con PID= "+str(r)+" Lo voy a matar"
            print m
            self.mis_variables.mensajes(m,"Log","green")
	    mando='kill -9 '+str(r)
	    print mando
	    os.system(mando)
        else:
            m="Polima NO esta corriendo, bye"
            self.mis_variables.mensajes(m,"Log","rojo")
            
            print m

############################################################################
    def __del__(self):
	print "********************* Destroy filtros_polima CLASS ***********************************"
        print "cerrando Polima Gui "
	self.kill_gui_polima()
        
############################################################################
