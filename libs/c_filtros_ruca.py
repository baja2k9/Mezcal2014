#!/usr/bin/env python

from  c_util import *
from c_cliente import *
import SocketServer
import c_filtros
from c_filtros import *
import c_util

import threading 
import thread
import gobject
import string
#import time
#gobject.threads_init()

#poner sockectserver en programa principal y mandar datos a procesa_respuesta

#V0.2, E. Colorado, prueba inicial
#V0.3, E. Colorado, Sep,2010, cambie envio de queue tipo tupples a strings
#v0.4  E. Colorado, Sep,2010, sume 1 a la posicion de envio
#v0.5  E. Colorado, Oct,2010, uso el ultimo archivo *.fil modificado
###########################################################

class RUCA(UTIL,CLIENTE,FILTROS):
    'Manejo de la rueda de Filtros RUCA'
    
    
###########################################################
    def __init__(self,variables):
        FILTROS.__init__(self)
        print "clase Ruca Ready..."
        self.ip="192.168.0.2"
        self.puerto=4966
        self.ip="localhost"
        self.usuario="ruca"
        self.mis_variables = variables
        self.numero_filtros=8
        self.extension='*.fil'
        self.p_name="Ruca Files (.fil)"
        self.puerto_respuestas=4967
        self.archivo_filtros="/usr/local/instrumentacion/bin/ruca.fil"
        util=c_util.UTIL()
        mando='ls -r --sort=time  /usr/local/instrumentacion/bin/*.fil |tail -n 1'
        r=util.ejecuta(mando)
        #print r
        if len(r) >3:
            #self.archivo_filtros='/usr/local/instrumentacion/bin/'+r
            self.archivo_filtros=string.strip(r)
        print "archivo ruca",self.archivo_filtros
            
###########################################################
    def pide_posicion(self):
        print 'Ruca pidiendo posicion...'
        data,status=self.manda_sin_respuesta("posicion")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,Color='rojo')
            return -1
        return True

###########################################################
    def mueve_filtros(self,posicion):
        print "Moviendo filtros ruca a posicion ",posicion
        t="filtro %d "% (posicion-1)
       
        data,status=self.manda_sin_respuesta(t)
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,Color='rojo')
            return -1
        #prueba
        #tupla = ["MSJ", data, "verde"]
        #self.mis_variables.queue.put(tupla)
        return True
###########################################################
    def procesa_respuesta(self,data):
        print "procesando respuesta ruca =>",data
        mando=data.split()
        key=mando[0]
        if key=="filtro":
            print "llego filtro RUCA"
            filtro= mando[1:]
            self.filtro=" ".join(filtro)
            print "el filtro Actual de RUCA es=",self.filtro
            #tupla = ["RUCA_UPDATE "+self.filtro]
            txt="RUCA_UPDATE "+self.filtro
            self.mis_variables.queue.put(txt)
        elif key=="termine":
            print "Ya terminio el movimiento de filtros, voy a pedir posicion!!!"
            self.pide_posicion()
            #self.mis_variables.queue.put(["RUCA_DONE","",""])
            self.mis_variables.queue.put("RUCA_DONE")
############################################################################

##class RUCAHANDLER(SocketServer.StreamRequestHandler,RUCA):
##    def __init__(self, variables):
##        self.mis_variables =  variables
##        
##    def handle(self):
##        # self.rfile is a file-like object created by the handler;
##        # we can now use e.g. readline() instead of raw recv() calls
##        self.data = self.rfile.readline().strip()
##        #self.data = self.rfile.readline()
##        print "SERVER RUCA >>>>>%s wrote:" % self.client_address[0]
##        print self.data
##        #procesar respuesta
##        self.procesa_respuesta(self.data)

'''a=RUCA()
HOST, PORT = "0.0.0.0", a.puerto_respuestas
# Create the server, binding to localhost on port 9999
print "Server con puerto", PORT
  
SocketServer.allow_reuse_address= True
server = SocketServer.TCPServer((HOST, PORT), MyRespuestasHandler)

#server.serve_forever()
thread.start_new(server.serve_forever, tuple())
print "servidor corriendo"
        
a.mueve_filtros(7)
#time.sleep(5)
#a.pide_posicion()
time.sleep(10)'''