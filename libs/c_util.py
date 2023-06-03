#!/usr/bin/env python
# -*- coding: utf-8 -*-

#V0.1, 2010    , E. Colorado ->inicio
#V0.2, Oct-2011, E. Colorado -> se agrego checa_proceso y is_running
#V0.3, Feb-2012, E. Colorado -> se agrego kill_pid_list

import os
from subprocess import *
import glob
import socket
import re
import math
#################################################################################################
class UTIL:
    "Clase de utilierias de archivos, etc"
    "V0.3 E. Colorado, inicio Febrero, 2010"

    debug=False
################################################
    def __init__(self):
        pass
        #print "util ready..."

#################################################################################################
    def ejecuta(self,cmd):
        bufsize=1024
        try:
            proceso =  Popen(cmd, shell=True, bufsize=bufsize, stdout=PIPE)
            pipe = proceso.stdout
            s1=pipe.read()
            pipe.close()
        except:
            print "hubo error"
            return -1

        #print 'Proceso pid' ,proceso.pid
        if not (len(s1 ) > 0) : return 0
        return s1

#################################################################################################
    def busca_archivo(self,dir,nombre_base):
        #buscar el ultimo archivo de imagen son el formato deseado

        if self.debug: print "buscando ultimo archivo en",dir," con nombre",nombre_base
        #juntar path + nombre
        archivo=os.path.join(dir,nombre_base)
        if self.debug: print "trayectoria completa=",archivo
        #formato="%s*[0-9]*.*" % archivo
        formato="%s[0-9]*.*" % archivo
        if self.debug: print "formato=",formato
        lista=glob.glob(formato)
        if self.debug: print "numero de elementos=",len(lista)
        if len(lista)<1:
            return nombre_base,0
        lista.sort()
        if self.debug: print lista
        ultima=lista[-1]
        if self.debug: print "ultima=",ultima
        #sacar nombre base
        base=os.path.basename(ultima)
        #quitar extension
        nombre,ext=os.path.splitext(base)
        if self.debug: print "nombre",nombre
        #sacar el numero ultimo
        nbase=len(nombre_base)
        numero=nombre[nbase:]
        if self.debug: print "numero",numero
        #quitar ultima letra
        if numero[-1].isalpha():
            #print "tiene caracter"
            numero=numero[0:-1]
        else:
            print "NO tiene caracter"

        #print "numero",numero
        #convertir a entero
        try:
            numero=int(numero)
        except:
            print "no encontre numero ultimo"
            numero=0
        if self.debug: print "numero",numero
        return ultima,numero
#################################################################################################
    def checa_es_archivo(self,dir,nombre_base,imagen):
        #print "Verificando archivo ",imagen
        existe=os.path.isfile(imagen)
        #print imagen," existe?",existe
        return existe

#################################################################################################
#################################################################################################
    def ping(self,ip, msg):
    #ip -a probar
    #msg- texto para saber a que sistema estamos probando
    #cuando estatus=0 todo esta bien
        print "ping to ",ip," msg=",msg
        mando="ping -q -c 1 "+ip
        #a=ejecuta(mando)
        status=os.system(mando)
        print "regreso ",status
        if status==0:
            print "ping "+msg+" GOOD"
        else:
            print "ping "+msg+" BAD"
            status=1
        return status
#################################################################################################
    def test_socket(self,ip,puerto, msg):
        #checa conexion a socket con timeout
        #resgresa: socket,True or False
        timeout=2

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, puerto))
            return (s, True)
        #except :
        except socket.error, netmsg:
            #print "Error de conexion ",netmsg, " en ",msg
            s = 'None'
            mierror=str(netmsg)+" ip="+ip+" pto="+str(puerto)+" =>"+msg
            return (s,mierror)

#################################################################################################
    def checa_proceso(self,programa):

        #print "checando proceso de programa",programa
        cmd="pgrep -l -f \"%s\""%(programa)
        #print cmd
        rx=self.ejecuta(cmd)
        #print rx
        #quitar /n
        #V1.3
        proceso =0

        tipo=str(type(rx))
        if tipo.find("str")>0:
            #print "si es string"
            rx=rx.strip()
            #verificar si en lista esta el propio pgrep
            rx = rx.split("\n")
            conta=0
            for a in rx:
                #print "renglon=",a
                if 'pgrep' in a:
                        print "se autodetecto pgrep, removing....."
                        del rx[conta]
                conta+=1
            num=len(rx)
            if num>0 :
                id=rx[0].split()
                id=id[0]
                #print "proceso=" ,id
                proceso=int(id)
        else:
            proceso =0
        #print "proceso",proceso
        return proceso
#################################################################################################
    def is_running(self,programa):
        #ver rutina anterior, casi lo mismo
        proceso=self.checa_proceso(programa)
        if proceso >0:
            return True
        else:
            return False
#################################################################################################
    def kill_pid_list(self,pid):
        #genera una lista con los pid que habrimos para luego matarlos
        print "appending pid=",pid," to kill list"

        try:
            fd = open("/tmp/kill_list.lst", "a")
        except:
            print "Problemas con archivo /tmp/kill_list.lst"
            return -1

        data='kill -9 %d \n'%pid
        print data
        fd.write(data)
        fd.close


#################################################################################################
    def my_beep(self):
        #por bug de ubuntu, no sirve print \a
        os.system('beep')
#################################################################################################
    def separa(s, thou=",", dec="."):
        integer, decimal = s.split(".")
        integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
        return integer + dec + decimal
#probar
#a=UTIL()
#a.busca_archivo('/slack/imagenes','spm')
#ultima,numero=a.busca_archivo('/slack/imagenes','image')
#ultima,numero=a.busca_archivo('/home/observa/imagenes','spm')
#print "ultima=",ultima, ", numero=",numero
