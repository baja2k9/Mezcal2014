#!/usr/bin/env python
# -*- coding: utf-8 -*-
# E. Colorado -V0.2 update nueva electronica de murillito con posicion electronica de la rendija
# OJO el rabit no permite 2 comunicaciones mas rapidas que 3 segundos

import string
import time
from c_cliente import *
###########################################################
class LAMPARAS(CLIENTE):
    'Manejo de las lamparas del echelle y del boller'
    PASOSXREV = 400          # Numero de pasos por revolucion del motor
    MICRMXREV = 50           # Numero de micrometros por revolucion del micrometro
    OFFSETCER = 0            # offset entre l sw de inicio y el cero del micrometro en pasos

    def __init__(self,variables=None):
        self.usuario="Echelle"
        self.debug=False
        self.ip="192.168.0.24"
        self.puerto=2020
        self.mis_variables = variables
        self.status=''
        self.posicion=-1
        self.lee_parametros()
        self.lamp_name='Bad?'

###########################################################
    def estado(self):
        print 'echelle o boller pidiendo estatus...'
        #puede ser Lampara1 (CuAr),Lampara2 (Planos) o Fuera
        data,status=self.manda("ESTATUS;" )
        if not status:
                print "bad"
                print data
                self.mis_variables.mensajes(data,"Log","rojo")
                return -1
        print "recibi",data
        self.status=data.strip('\n')
        print 'status=',self.status,' len=',len(self.status)
        
        if self.status =='Lampara1':
            self.lamp_name='CuAr'
        elif self.status =='Lampara2':
            self.lamp_name='Planos'
        else:
            self.lamp_name='None'
        print 'Lampara=',self.lamp_name
        
        #por que el rabitt es muy lento
        time.sleep(2)
        

###########################################################
    def saca_lamparas(self):
        print 'echelle pidiendo estatus...'
        data,status=self.manda('FUERA_LAMPARAS;' )
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
            return -1
        print "recibi",data
        return data

###########################################################
    def mete_lamparas(self,pos=1):
        print 'echelle mete lampara ',pos
        cmd='LAMPARA%d;'%(pos)
        print cmd
        data,status=self.manda(cmd )
        if not status:
                print "bad"
                print data
                self.mis_variables.mensajes(data,"Log","rojo")
                return -1
        print "recibi",data

###########################################################
    def preexpone(self,tipo=None):
        print "pre expone del boller o echelle, tipo",tipo

###########################################################
    def postexpone(self):
        pass
###########################################################
    def lee_parametros(self):
        #f = open('/usr/local/instrumentacion/lamparas_boller/boller.cfg')
        f = open('/usr/local/boller_sbig/boller.cfg')
        linea = f.readline()
        while len(linea):
            if linea.rfind("Pasos por revolucion") == 0:
                tup = linea.partition(":")
                self.PASOSXREV = string.atoi(tup[2])
                print 'Pasos por rev:',self.PASOSXREV
            if linea.rfind("Micrometros por revolucion") == 0:
                tup = linea.partition(":")
                self.MICRMXREV= string.atoi(tup[2])
                print 'Micrometros por Rev', self.MICRMXREV
            if linea.rfind("Offset del cero") == 0:
                tup = linea.partition(":")
                self.OFFSETCER = string.atoi(tup[2])
                print 'Offset cero', self.OFFSETCER
            linea = f.readline()
        f.close()
###########################################################
    def  Pide_posicion_rendija(self):
        #por que el rabitt es muy lento
        time.sleep(1)
        data,status=self.manda("dame_posicion_motor_rendija;" )
        if not status:
                print "bad"
                print data
                try:
                    self.mis_variables.mensajes(data,"Log","rojo")
                except:
                    print "No pude reportar error al GUI"
                return -1
        print "recibi",data
        self.posicion=data.strip('\n')
        self.posicion=((string.atoi(data)-self.OFFSETCER)*self.MICRMXREV/self.PASOSXREV)
        print 'posicion=',self.posicion

###########################################################
'''
a=LAMPARAS()
a.DEBUG=True
a.estado()
a.Pide_posicion_rendija()
'''