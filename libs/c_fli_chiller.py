#!/usr/bin/env python
from c_cliente import *
import time

#V0.1, E. Colorado, Marzo 2011, incial

###########################################################
class FLI_CHILLER(CLIENTE):
    'Manejo de compresor kinetics de la FLI'

###########################################################
    def __init__(self):

        self.usuario="FLI kinetics Chiller"

        self.ip="192.168.3.70"
        self.puerto=10001
        self.set_timeout(3)
        self.debug=True
        #self.manda("POLL\r")
        #time.sleep(1)
        self.is_running=False
        self.temp=0.0
        self.alarma=0
        self.setpoint=0

        self.lista_alarma=[
            "Ok, No alarma",
            "Bajo Nivel de liquido",
            "Bajo flujo del liquido",
            "Insuficiencia de agua del cooler",
            "Etapa 1 de refrigeracion sin alimentacion",
            "Etapa 2 de refrigeracion sin alimentacion",
            "La bomba no tiene alimentacion, checa el fusible",
            "Usando sensor remoto, el cual esta en circuito abierto",
            "Alarma de temperatura Alta",
            "Alarma de temperatura Baja",
            "Etapa 1 de refrigeracion sin alimentacion",
            "Sobre Temperatura",
            "4-40mA Alarm",
        ]

###########################################################
    def pide_temp(self):
        if self.debug: print 'Chiller pidiendo temp'
        self.send_data('PT?')

###########################################################
    def pide_ready(self):

        data,status=self.manda("READY?\r")
###########################################################
    def start(self):
        self.send_data('START')
###########################################################
    def stop(self):
        self.send_data('STOP')
###########################################################
    def is_start(self):
        self.send_data('START?')
###########################################################
    def checa_alarmas(self):
        self.send_data('ALMCODE?')
###########################################################
    def get_setpoint(self):
        self.send_data('SP?')
###########################################################
    def send_data(self,data):
        print "sendind to chiller:",data
        socket,status=self.manda_open(data+"\r")
        if status:
            socket.setblocking(1)
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_chiller(socket)
            print 'cerrando socket chiller'
            socket.close()
        else:
            print "Error al mandar datos al chiller de FLI"

############################################################################
    def lee_chiller(self,socket):
        print "en lee chiller"

        data=''
        while 1:
            c = socket.recv(1)
            #print repr(c)
            data+=c
            #print "------------->", data
            if c=='!':
                #print "Ya llego el fin"
                #leer ultimo \r
                basura=socket.recv(1)
                data+='\r'
                #print "------------------------"
                break
        print "Terminalos lectura FLI Chiller"
        d2=data.split('\r')
        for x in d2:
            self.procesa_respuesta_chiller(str(x))
##########################################################################
    def procesa_respuesta_chiller(self,data):
        if len (data)<1: return
        print "procesando chiller data", data,"(",len(data),")"
        if data[0]=='F':
            ############################################
            ##funciones
            print "Es una funcion"
            f=data[1:4]
            print 'f=',f
            if f=='043':
                #pt, temperatura
                temp=data[5:-1]
                print "temp->",temp
                try:
                    self.temp=float(temp)
                except:
                    print 'bad temp'

            elif f=='060':
                #start?
                is_running=data[5:-1]
                print "is running->",is_running
                try:
                    x=float(is_running)
                    if x<0:
                        self.is_running=True
                    else:
                        self.is_running=False
                except:
                    print 'bad status'

            elif f=='076':
                #alarmas
                alarma=data[5:-1]
                print "alarma->",alarma
                try:
                    self.alarma=int(float(alarma))
                except:
                    print 'bad alarm'
            elif f=='057':
                #sp?, setpoint
                s=data[5:-1]
                print "set point->",s
                try:
                    self.setpoint=float(s)
                except:
                    print 'bad get set point'
        ##################################################
        ##Errores
        elif data[0]=='E':
            print "Es un Error"

##########################################################################
    def info(self):
        print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        print 'FLI chiller info:\n'
        print 'ip=',self.ip
        print 'puerto=',self.puerto
        print 'is_running=',self.is_running
        print 'temp=',self.temp
        print 'Set point=',self.setpoint
        print 'codigo alarma=',self.alarma, '-->',self.lista_alarma[self.alarma]

        print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'

##########################################################################
print "------------------------------------------------"
a=FLI_CHILLER()

a.stop()
time.sleep(1)

print "------------------------------------------------"
time.sleep(1)
#a.start()
print "------------------------------------------------"
#time.sleep(10)
a.is_start()
time.sleep(2)
print "------------------------------------------------"
a.pide_temp()
print "------------------------------------------------"
time.sleep(2)
a.checa_alarmas()
time.sleep(1)
a.get_setpoint()
a.info()
