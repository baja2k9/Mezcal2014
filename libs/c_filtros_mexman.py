
#sudo apt install mosquitto mosquitto-cliente
#pip install paho-mqtt

import os
import paho.mqtt.client as mqtt
import json
import time
import c_filtros
from c_filtros import *
###########################################################
'''
RUEDA 1 VA DE POS 1 AL 8
RUEDA 2 VA DE POS 9 AL 16

YA SE CONTROLAN POR SEPARADO DEL 1 AL 8
SE TARDA ENTRE 8 Y 9 SEGUNDOS AL PASAR DE UNA POSICION A OTRA
Se MUEVE POR LA DISTACIOA MAS CORTA, PEOR DE LOS CASOS 25 SEGUNDOS
'''
class MEXMAN(FILTROS):
    'Manejo de secundario 84 modo mqttp'

###########################################################
    def __init__(self,variables):
        print ('Arrancando clase mexman con mqtt')
        FILTROS.__init__(self)
        self.mis_variables = variables  #callback
        self.mqtt_server='localhost'


        self.mosquitto = mqtt.Client()
        self.mosquitto.connect(self.mqtt_server, 1883, 60)



        self.mosquitto.on_message = self.on_message
        self.mosquitto.on_publish = self.on_publish
        self.mosquitto.on_connect = self.on_connect
        self.mosquitto.on_disconnect = self.on_disconnect

        self.mosquitto.loop_start()





        self.numero_filtros = 8
        self.extension = '.cfg'
        self.usuario = "mexman"

        self.l_rueda1 = []  # generar nueva lista
        self.l_rueda2 = []  # generar nueva lista
        self.f1 = 0
        self.f1_name = "?"
        self.f2 = 0
        self.f2_name = "?"
        self.filtro = "no se"  # aqui estan los 2 nombres de los filtros

        #self.filter_name="/home/observa/filtros.cfg"
        self.archivo_filtros = "filtros.cfg"
        homedir = os.path.expanduser('~')
        self.archivo_filtros = os.path.join(homedir, self.archivo_filtros)
        print( "archivo de filtros Mexman", self.archivo_filtros)
        self.autoLoadFilterFile()
        self.debug = False
        self.t_max = 40  # segundos

    ###########################################################
    def espera1(self, pos):
        t = ti = time.time()
        print 'mexman espera1 a pos', pos

        while True:
            time.sleep(0.5)
            t = time.time()
            print "espera1 en pos %d esperando a pos %d, han pasado %3.3f segundos" % (self.f1, pos, t - ti)
            if self.f1 == pos: break
            if t - ti > self.t_max:
                print 'Timeout en rueda1 de Mexman'
                break

    ###########################################################
    def espera2(self, pos):
        t=ti=time.time()
        print 'mexman espera2 a pos', pos

        while True:
            time.sleep(0.5)
            t = time.time()
            print "espera2 en pos %d esperando a pos %d, han pasado %3.3f segundos"%(self.f2,pos,t-ti)
            if self.f2 == pos: break
            if t-ti>self.t_max:
                print 'Timeout en rueda2 de Mexman'
                break

    ###########################################################
    def mueve_rueda1(self, pos):
        print ('mover rueda 1 a pos=',pos)

        self.publica_mosquitto(pos,'oan/tel84/control/mexman/move/wheel/1')

    ###########################################################
    def mueve_rueda2(self, pos):
        print('mover rueda 2 a pos=', pos)

        self.publica_mosquitto(pos, 'oan/tel84/control/mexman/move/wheel/2')

    ###########################################################
    def publica_mosquitto(self,msg,topic='oan/tel84/control/mexman'):

        try:
            self.mosquitto.publish(topic, msg)
        except:
            print ('WTF, Error al publicar en mosquitto',msg)

    ###########################################################
    def on_publish(self, client, userdata, mid):
        #print('Ya mande a publicar', userdata, mid)
        pass

    ###########################################################
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.mosquitto.subscribe("oan/tel84/control/mexman/positions")

    ###########################################################
    def on_message(self,client, userdata, message):
        '''
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        '''

        data=str(message.payload.decode("utf-8"))
        d = json.loads(data)

        self.f1=int(d['wheel1'])
        self.f2 = int(d['wheel2'])

        self.f1_name=self.l_rueda1[self.f1-1]
        self.f2_name = self.l_rueda2[self.f2-1]

        self.filtro = "%s + %s" % (self.f1_name, self.f2_name)
        if self.debug: print ('Mexman:',self.filtro)

        #self.actualiza_posicion(data)

        #mandar a gui
        txt = "MEXMAN_UPDATE " + self.filtro
        self.mis_variables.queue.put(txt)
###########################################################
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Error, Unexpected disconnection.", rc)

        '''
        while (True):
            try:
                print("Trying to Reconnect")
                self.mosquitto.connect(self.mqtt_server, 1883, 60)
                break
            except:
                print("Error in Retrying to Connect with Broker")
                continue
        '''

###########################################################
    def inicializa(self):
        self.publica_mosquitto(1,'oan/tel84/control/mexman/init')

###########################################################
    def autoLoadFilterFile(self):
        try:
            openfile = open(self.archivo_filtros, 'r')
        except:
            a = "Error autoload can't open " + self.archivo_filtros
            print
            a
            #self.mi_ccd.mis_variables.mensajes(a, "Log", "rojo")
            return

        a = "Usando archivo de filtros= " + self.archivo_filtros


        str = openfile.read()
        openfile.close()
        t = str.split('\n')
        print (t)


        self.l_rueda1 = t[0:8]
        self.l_rueda2 = t[8:]
        print ('rueda1',self.l_rueda1)
        print('rueda2', self.l_rueda2)

###########################################################
    def pide_posicion(self):
        pass

###########################################################
    def mueve_filtros(self,posicion,espera=True):
        print "moviendo filtros Mexman a posicion ",posicion
        if posicion > 16:
            print'Error al querer mover a una posicion inexistente'
            return False

        if posicion < 1:
            print'Error al querer mover a una posicion inexistente'
            return False

        if posicion>8:
            pos=posicion-8
            self.mueve_rueda2(pos)
            if espera:
                # vamos a esperar mexman
                self.espera2(pos)
        else:
            self.mueve_rueda1(posicion)
            if espera:
                # vamos a esperar mexman
                self.espera1(posicion)

###########################################################

###########################################################

###########################################################
if __name__ == "__main__":

    a=MEXMAN(None)
    a.mueve_filtros(8, True)
    a.mueve_filtros(9,True)
    #time.sleep(2)

    print 'pos 1=',a.f1
    print 'nombre 1=',a.f1_name
    print 'pos 2=',a.f2
    print 'nombre 2=',a.f2_name
    print 'filtro=',a.filtro
