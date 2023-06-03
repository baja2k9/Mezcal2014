#!/usr/bin/env python
# -*- coding: utf-8 -*-

from  c_util import *

import c_cliente
from c_cliente import *

from c_filtros import *
import time
import gtk

class ESPECTROPOL(UTIL,CLIENTE,FILTROS):
    'Manejo de la mesa angular del espectropolarimetro'
    numero_filtros=7
    extension='*.cfg'
    #archivo_filtros="~/polima.cfg"
    archivo_filtros="polima2_fli.cfg"
    p_name="Polima Files (.cfg)"
    usuario="espectropolarimetro"
    DEBUG=True
    __error=0.05
#------------------------------------------------------------------------------
    def __init__(self,variables):
        print "espectropolarimetro ready"
        self.mis_variables = variables
        self.filtro_pos=-1
        self.filtro=-1
        #self.pre_filtro=-1
        self.polpos=-1
        self.angulo=-1
        self.mesa_pos="HOME"
        self.pol_estado=' ?'

        #7 filtros de la rueda del FLI
        #mejor los leo como todos los demas via archivo
        self.rueda_list=["U", "B","V","R","I","Ha","Vacio"]
        homedir = os.path.expanduser('~')
        self.archivo_filtros=os.path.join(homedir,self.archivo_filtros)
        print "archivo de filtros polima2",self.archivo_filtros

        self.txt_callback=None

        #FLI
        #self.ip, self.puerto = "localhost", 9710
        self.ip, self.puerto = "192.168.0.32", 9711
        #polima2 server de la mesa angular y lienal
        #cliente2
        self.polima2=c_cliente.CLIENTE()
        self.polima2.ip=self.ip
        self.polima2.puerto=self.puerto

        #inicializar todo
        #arrancar servidor
        self.arranca_beagle()
        #self.lineal.full_init()
        #self.angular.full_init()
        #self.init_filtros()

#------------------------------------------------------------------------------
    def __del__(self):
        print "cerrando driver de espectropolarimetro"
        #del lineal
        #del angular
#------------------------------------------------------------------------------
    def arranca_beagle(self):
        print 'arrancando beagle'
        bb = c_cliente.CLIENTE()
        bb.ip = self.ip
        bb.puerto = 4950
        bb.manda_sin_respuesta('hola')
        time.sleep(2)
        print 'beagle ok'

    # ------------------------------------------------------------------------------
    def mueve_filtros(self,filtro):
        #la rueda usa filtros de 0-6
        #pero la gui de 1-7
        #print "moviendo filtro a",filtro
        a="SET_FILTER_POS %d \n"%(int(filtro)-1)
        print a
        #self.txt_callback(a,'verde')


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


#------------------------------------------------------------------------------
    def posicion_filtros(self):
        print 'espectropol pidiendo posicion...'

#------------------------------------------------------------------------------
    def posicion_pol(self ):
        data,status=self.polima2.manda("POL_POS ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print 'data=',data
        data=data.split()
        try:
            self.angulo=float(data[1])
        except:
            self.angulo=-1.0
        self.angulo=round(self.angulo,2)
        print "el angulo del polarizador de polima2 es",self.angulo
        self.polpos=self.angulo

# ------------------------------------------------------------------------------
    def status_pol(self):
        data, status = self.polima2.manda("POL_STATUS ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data, "Log", "rojo")
            return -1
        print 'data=', data
        data = data.split()
        try:
            self.angulo = float(data[1])
        except:
            self.angulo = -1.0
        self.angulo = round(self.angulo, 2)
        estado=str(data[2:])
        print "el angulo del polarizador de polima2 es", self.angulo, 'status',estado
        self.pol_estado=estado
        self.polpos = self.angulo

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
        self.mesa_pos="HOME"
#------------------------------------------------------------------------------
    def lineal_init_soft(self ):

        self.mesa_pos="HOME"

#------------------------------------------------------------------------------
    def move_in(self ):

        self.mesa_pos="IN"

#------------------------------------------------------------------------------
    def move_out(self ):

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
            #self.posicion_pol()
            self.status_pol()
            self.mis_variables.update_pol2()
            self.mis_variables.gui_update()
            while gtk.events_pending(): gtk.main_iteration()
            time.sleep(0.2)
            if self.angulo==deseado: break
            if self.angulo >a and self.angulo<b:
                print "polima llego..."
                loop=0
                break
            else:
                print "polima no ha llegado , actual="+str(self.angulo)

#------------------------------------------------------------------------------
