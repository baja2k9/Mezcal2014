#!/usr/bin/env python
# -*- coding: utf-8 -*-
#V0.2 Sep. 2017, anexe circulo en ds9
from  c_util import *

import c_cliente
from c_cliente import *

from c_filtros import *
import time
import os
import os.path

import c_ds9
from c_ds9 import *

class POLIMA2(UTIL,CLIENTE,FILTROS):
    'Manejo de polima2 filtros y polarizador y mesa lineal'
    numero_filtros=7
    extension='*.cfg'
    #archivo_filtros="~/polima.cfg"
    archivo_filtros="polima2_fli.cfg"
    p_name="Polima Files (.cfg)"
    usuario="polima2"
    DEBUG=True
    __error=0.05
#------------------------------------------------------------------------------
    def __init__(self,variables):
        print "polima2 ready"
        self.mis_variables = variables
        self.filtro_pos=-1
        self.filtro=-1
        #self.pre_filtro=-1
        self.polpos=-1
        self.angulo=-1
        self.mesa_pos="HOME"

        #7 filtros de la rueda del FLI
        #mejor los leo como todos los demas via archivo
        self.rueda_list=["U", "B","V","R","I","Ha","Vacio"]
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros polima2",self.archivo_filtros

        self.txt_callback=None

        #FLI
        #self.ip, self.puerto = "localhost", 9710
        self.ip, self.puerto = "192.168.0.41", 9710
        #polima2 server de la mesa angular y lienal
        #cliente2
        self.polima2=c_cliente.CLIENTE()
        self.polima2.ip=self.ip
        self.polima2.puerto=self.puerto+1

        #inicializar todo
        #self.lineal.full_init()
        #self.angular.full_init()
        #self.init_filtros()
        homedir = os.path.expanduser('~')
        self.archivo_cfg=os.path.join(homedir,"polima2_instrumento.cfg")
        print "Archivo de configuracion polima2",self.archivo_cfg

        self.x=512*2
        self.y=517*2
        self.r=252*2
        self.pol = c_ds9.DS9()
        self.read_config()
        

#------------------------------------------------------------------------------
    def __del__(self):
        print "cerrando driver de polima2"
        #del lineal
        #del angular
#------------------------------------------------------------------------------
    def mueve_filtros(self,filtro):
        #la rueda usa filtros de 0-6
        #pero la gui de 1-7
        #print "moviendo filtro a",filtro
        a="SET_FILTER_POS %d \n"%(int(filtro)-1)
        print a
        #self.txt_callback(a,'verde')
        data,status=self.manda(a)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data

#------------------------------------------------------------------------------
    def mueve_pol(self,pos,auto=True):
        print "moviendo polarizador a",pos
        a="MOVE_POL %f \n"%(pos)
        print a
        data,status=self.polima2.manda_sin_respuesta(a)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        
        if auto:
            self.espera_pol(pos)
        return True
#------------------------------------------------------------------------------
    def init_filtros(self):
        print "******** init FLI filter Wheel ***********"
        t,s=self.manda("INIT_FILTERS ")
        if not s:
            print "bad"
            print t
            #self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        #t=t.split()
        #self.power=float(t[1])
        print t

#------------------------------------------------------------------------------
    def posicion_filtros(self):
        if self.DEBUG: print 'polima pidiendo posicion...'
        data,status=self.manda("GET_FILTER_POS ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        print len(data)
        data=data.split()
        print data
        try:
            self.filtro_pos=int(data[1])
        except:
            self.filtro_pos=0
            self.mis_variables.mensajes('Error pide pos fli filter'+str(data[1]),"Log","rojo")
        print "el numero de filtro es",self.filtro_pos
        self.filtro=self.rueda_list[self.filtro_pos]
        print "el filtro es",self.filtro
        txt="MEXMAN_UPDATE "+self.filtro
        print self.mis_variables
        print txt
        self.mis_variables.queue.put(txt)
#------------------------------------------------------------------------------
    def posicion_pol(self ):
        data,status=self.polima2.manda("POL_POS ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        data=data.split()
        self.angulo=float(data[1])
        self.angulo=round(self.angulo,2)
        print "el angulo del polarizador de polima2 es",self.angulo
        self.polpos=self.angulo

#------------------------------------------------------------------------------
    def pide_posicion (self):
        #lo puse por compatibilidad
        self.posicion_filtros()
#------------------------------------------------------------------------------
    def pol_init(self ):
        data,status=self.polima2.manda("INIT_ANGULAR ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
#------------------------------------------------------------------------------
    def pol_init_soft(self ):
        data,status=self.polima2.manda("INIT_ANGULAR_SOFT ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data

#------------------------------------------------------------------------------
    def lineal_init(self ):
        data,status=self.polima2.manda("INIT_LINEAL ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        self.mesa_pos="HOME"
#------------------------------------------------------------------------------
    def lineal_init_soft(self ):
        data,status=self.polima2.manda("INIT_LINEAL_SOFT ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        self.mesa_pos="HOME"

#------------------------------------------------------------------------------
    def move_in(self ):
        data,status=self.polima2.manda("MOVE_IN ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        self.mesa_pos="IN"

#------------------------------------------------------------------------------
    def move_out(self ):
        data,status=self.polima2.manda("MOVE_OUT ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print data
        self.mesa_pos="OUT"
#------------------------------------------------------------------------------
    def espera_pol(self,deseado):
        if self.DEBUG: print "esperando pol a",deseado
        a=deseado-self.__error
        b=deseado+self.__error

        print "movi polima a %f con errores posibles %f , %f"%(deseado,a,b)

        loop=1
        while loop:
            time.sleep(0.8)
            #data,status=self.manda_sin_respuesta("POL_POS ")
            self.posicion_pol()
            self.mis_variables.update_pol2()
            self.mis_variables.gui_update()
            time.sleep(0.1)
            if self.angulo==deseado: break
            if self.angulo >a and self.angulo<b:
                print "polima llego..."
                loop=0
                break
            else:
                print "polima no ha llegado , actual="+str(self.angulo)

#------------------------------------------------------------------------------
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
###########################################################
    def postexpone(self,mi_ccd=None):
        #print "postexpone polima"
        self.pol.circle(self.x/mi_ccd.cbin-mi_ccd.xorg,self.y/mi_ccd.cbin-mi_ccd.yorg,self.r/mi_ccd.cbin)

