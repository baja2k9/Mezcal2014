#!/usr/bin/env python

#sudo apt install mosquitto mosquitto-cliente
#pip install paho-mqtt

import paho.mqtt.client as mqtt
from  c_util import *
from c_cliente import *
import time

import threading

#V2.0, E. Colorado, Mayo 2019, inicial con MQTT
###########################################################
class SEC84(UTIL,CLIENTE):
    'Manejo del secundario del 84'

    usuario="Secundario 84"
    #foco=-1
    _error=1.0
    DEBUG=True

###########################################################
    def __init__(self,variables):
        #self.ip="grulla"
        self.mis_variables = variables
        self.ip="localhost"
        self.puerto=9712
        self.foco=-1
        self.set_timeout(10)    #timeout para el secundario

        self.mqtt_server = 'localhost'

        self.mosquitto = mqtt.Client()
        self.mosquitto.connect(self.mqtt_server, 1883, 60)
        self.mosquitto.loop_start()

        self.mosquitto.on_message = self.on_message
        self.mosquitto.subscribe("oan/tel84/control/secondary/position")
        #self.pos = 1024
###########################################################
    def pide_posicion(self):

        print 'pide_posicion ya no se usa asi'
        return True

###########################################################
    def mueve(self,posicion):

        if self.DEBUG: print "Moviendo sec84 posicion ",posicion


        self.publica_mosquitto(posicion)
        return True

    ###########################################################
    def publica_mosquitto(self, msg, topic='oan/tel84/control/secondary/move'):

        try:
            self.mosquitto.publish(topic, msg)
        except:
            print('WTF, Error al publicar en mosquitto', msg)

    ###########################################################
    def on_message(self, client, userdata, message):
        #print("message received ", str(message.payload.decode("utf-8")))
        #print("message topic=", message.topic)
        #print("message qos=", message.qos)
        #print("message retain flag=", message.retain)

        try:
            pos = int(message.payload.decode("utf-8"))
        except:
            print("Error No pude obtener posicion")
            return
        self.foco = pos
        #print 'llego nueva posicion', pos
        #self.actualiza_posicion(pos)

    ###########################################################
    def espera(self, posicion):

        thread = threading.Thread(target=self.do_espera(posicion))
        thread.start()
        thread.join()
        print 'Ya termino la espera'

    ###########################################################
    def do_espera(self,posicion):
        a=posicion-self._error
        b=posicion+self._error
        print "esperando secundario a posicion",posicion, "error posible=",self._error
        print a,b

        conta=1
        while 1:
            time.sleep(1)
            #pedir posicion
            #self.pide_posicion()
            if self.foco==posicion:
                break
            if (self.foco>=a) and (self.foco<=b):
                print "secundario ya llego",self.foco
                break
            else:
                print "secundario No ha llego",self.foco

            conta+=1
        if self.DEBUG: print "termine espera foco84"

###########################################################
    def procesa_respuesta(self,data):

        #YA NO SE USA
        #print "procesando rx"
        mando=data.split()
        key=mando[0]
        if key=="Pos":
            self.foco=int(mando[1])
            if self.DEBUG: print "posicion sec84=",self.foco



############################################################################
'''
a=SEC84(None)
c=1234
a.pide_posicion()
a.mueve(c)
a.espera(c)
a.pide_posicion()
'''

