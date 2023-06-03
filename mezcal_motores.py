#!/usr/bin/env python
# -*- coding: utf-8 -*-

# V0.1 E. Colorado, inicial Jun-2014
# V0.2 E. Colorado, un sleep para el busy
# V0.3 E. Colorado, checa_error
import sys
import time
import c_config_mez
from c_config_mez import *

sys.path.append("libs")
from c_cliente import *

###########################################################
class MEZCAL_MOTORES(CLIENTE,CONFIGURA):
    'Manejo interno del instrumento Mezcal'

###########################################################
    def __init__(self,variables):
        CLIENTE.__init__(self)

        self.ip="192.168.0.26"
        self.puerto=10001
        #self.set_timeout(15)
        self.usuario='Mezcal'
        #self.lista_wheel = [ "Clear", "Pol 90" ,  "Pol 45" ,"Pol 0","RC"]
        self.lista_wheel = [ "Clear", "Clear" ,  "Clear"  ,"Clear","RC"]
        #self.lista_filtros = [ "Ha 90A","OIII 60A", "SII 90A"  ,"Vacio" ]
        self.lista_filtros = [ "Ha 90A","OIII 60A", "CO+"  ,"H2O" ]
        self.lista_lamparas = ["Off", "Tungsten","Th - Ar" ]
        self.lista_rejilla = [ "Rej 1", "Rej 2", "Rej 3", "Espejo" ]
        self.lista_rendijas = [ "70 microns", "150 microns" ,"Clear" ]
        self.lista_carro_pos=["OUT","IN"]

        #cargar lista de configuracion de archivo
        CONFIGURA.__init__(self)
        self.filtro=3
        self.eje_filtro=3

        #slit
        self.rendija=2
        self.eje_rendija=2

        self.wheel=1
        self.eje_wheel=1

        self.diffuser=0
        self.mirror=0
        self.slit=0
        self.grating=5
        self.estado_lamp=-1;self.lamp=0
        self.lamp_txt='??'
        self.shutter='Closed'
        self.shutter_mode='random'
        self.seguro_foco=-1
        self.busy=False #controla el pedir posicion

        self.rejilla_mes=-1
        self.lentes_mes=-1
        self.is_moving=0
        #self.debug=False
        self.error_mezcal='Ok'
        self.error_mez_contador=0
        self.debug=False
###########################################################
    def inicializa(self,eje):
        print 'inicializando eje %d del mezcal'%eje
        cmd=">:A%1d2;"%eje

        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def manda_mensaje (self,cmd):
        if self.debug: print 'tx:',cmd
        data,status=self.manda(cmd)
        if not status:
            print "bad"
            print data
            return -1
        #if self.debug:print 'rx:',data,'status:',status
        r=self.procesa_respuesta(data)
        return r
###########################################################
    def procesa_respuesta(self,data):
        # :A00003-A5C-111-17FD6;
        if self.debug: print "Procesando rx=",data,
        #print type(data)
        #print "len", len(data)
        
        if len(data) <5:
            print "NO llegaron datos completos"
            return -1
        if len(data) >23:
            print "llegaron datos multiples"
            return -2
        dato=data.strip(';')
        #dato=data[1:-1] #quito inicio y final
        dato=dato.strip(':')
        #print "dato stripeado=",dato
        mando=dato.split('-')
        #print mando
        cod=mando[0]
        cod=int(cod[1:],16)

        pot=mando[1]
        pot=int(pot,16)

        gin=mando[2]
        gin=int(gin,16)
        ints=mando[3]
        ints=int(ints,16)
        '''
        print 'cod',cod
        print 'pot',pot
        print 'gin',gin
        print 'ints',ints
        '''

        if cod > 32767:
            cod=cod- 65536
        self.rejilla_mes=cod

        self.lentes_mes=pot

        self.wheel=(gin & 0x0f) -1

        self.slit=( (gin &0x0f0) >> 4) - 1

        self.filtro=((gin &0xf00) >> 8) - 1

        pp =(ints & 0x200)
        if pp >0:
            self.seguro_foco=1
        else:
            self.seguro_foco=0

        pp =(ints & 0x100)
        if pp >0:
            self.shutter='Closed'
        else:
            self.shutter='Open'

        pp =(ints & 0x80)
        if pp >0:
            self.shutter_mode='Remote'
        else:
            self.shutter_mode='Local'

        pp =(ints & 0x60)
        if ( (pp == 0) or (pp == 0x60)):
            self.mirror=2
        else:
            if (pp==0x40): self.mirror=0
            if (pp==0x20): self.mirror=1

        pp =(ints & 0x18)
        if ( (pp == 0) or (pp == 0x18)):
            self.diffuser=2
        else:
            if (pp==0x10): self.diffuser=0
            if (pp==0x8): self.diffuser=1

        pp =(ints & 6)
        #print "pp=",pp
        if (pp==6): self.estado_lamp=1
        if (pp==4): self.estado_lamp=0;self.lamp=1
        if (pp==2): self.estado_lamp=0;self.lamp=2
        
        if self.estado_lamp==1:
            self.lamp_txt='OFF'
        elif self.lamp==1:
            self.lamp_txt='Tungsten'
        elif self.lamp==2:
            self.lamp_txt='Th-Ar'
            

        #print "procesa_respuesta OK"
        return 1
###########################################################
    def pide_posicion(self):
        self.busy=True
        cmd="<:A10;"
        r=self.manda_mensaje(cmd)
        time.sleep(0.1)
        self.busy=False
        return r
###########################################################
    def enciende(self,cual):
        #cual=0, lamp=2
        #cual=1, lamp=1
        #ambos casos
        #estado_lamp  = 0 (0=encendia 1=apagada)
        #lamp=2=Th-Ar
        #lamp=1=Tungsten
        lamp1=lamp2=1
        if cual==0:
            lamp1=0
        else:
            lamp2=0

        cmd=">:A72%1d%1d22;" % (lamp1,lamp2)
        self.casi_manda_sin_respuesta(cmd)

###########################################################
    def espejo_in(self):
        #mirror=1
        cmd=">:A722202;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def espejo_out(self):
        #mirror=0
        cmd=">:A722212;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def apaga(self):
        #estado_lamp  = 1
        cmd=">:A721122;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def cierra_shutter(self):
        #Closed
        cmd=">:A620011;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def abre_shutter(self):
        #shutter      = Open
        cmd=">:A620010;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def deshabilita_shutter(self):
        #shutter mode = Remoto
        print 'Modo Remoto'
        cmd=">:A620001;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def habilita_shutter(self):
        #shutter mode = Local igual a cerrar
        print 'Modo Local = Cerrar'
        cmd=">:A620011;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def detiene(self,eje):
        cmd=">:A%1d1;" % eje
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def difusor_in(self):
        cmd=">:A722220;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def difusor_out(self):
        cmd=">:A722221;"
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def libera(self,eje):
        cmd= ">:A%1d4;"% eje
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def mueve(self,eje,pos):
        print "mueve mes:",eje,pos
        npos=pos+1

        if eje==1:
            if npos >5: npos=5

        if eje==2:
            if npos >3: npos=3

        if eje==3:
            if npos >4: npos=4


        cmd=  ">:A%1d3%04d;"% (eje, npos)
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def mueve_lentes(self,pos):
        if pos <1864: pos=1860
        if pos >3097: pos=3100

        print 'moviendo lente a',pos
        cmd= ">:A43%04X;"% pos
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def mueve_rejilla(self,pos):
        if pos <-75: pos=-75
        if pos >75: pos=75

        cmd= ">:A53%04X;"% (pos&0xFFFF)
        self.casi_manda_sin_respuesta(cmd)
###########################################################
    def mezcal_info(self):

        print "seguro foco  =",self.seguro_foco
        print "shutter      =",self.shutter
        print "shutter mode =",self.shutter_mode
        print "mirror       =",self.mirror
        print "diffuser     =",self.diffuser
        print "estado_lamp  =",self.estado_lamp,self.lamp_txt
        print "lamp         =",self.lamp
        print "lentes_mes   =",self.lentes_mes
        print "rejilla_mes  =",self.rejilla_mes
        print "wheel        =", self.wheel,self.lista_wheel[self.wheel]
        print "slit         =",self.slit,self.lista_rendijas[self.slit]
        print "filtro       =",self.filtro,self.lista_filtros[self.filtro]
        print "is moving    =",self.is_moving


###########################################################
    def casi_manda_sin_respuesta(self,cmd):
        print 'tx:',cmd
        self.busy=True
        #time.sleep(0.1)
        self.manda_sin_respuesta(cmd)
        #time.sleep(0.1)
        self.busy=False
###########################################################
    def checa_errores (self):
        
        data,status=self.manda("dame_error")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug:print 'rx:',data,'status:',status
        data=data.strip()
        if data=='OK':
            #print "No hay errores"
            r=0
        else:
            print "Error en Mezcal:",data
            self.error_mez_contador+=1
            self.error_mezcal=data
            r=-2
        
        return r
###########################################################
#m=MEZCAL_MOTORES(None)
#m.pide_posicion()
#m.checa_errores()
