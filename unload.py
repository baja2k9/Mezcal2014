#!/usr/bin/python
import subprocess
from subprocess import *
import sys
import string

class UNLOAD(object):
    
    def __init__(self):
        pass
        print "clase unload pasa matar procesos V0.2"
 #######################################################################
    def ejecuta(self, cmd):
        bufsize=1024
        try:
            proceso =  Popen(cmd, shell=True, bufsize=bufsize, stdout=PIPE)
            pipe = proceso.stdout
            s1=pipe.read()
            pipe.close()
        except:
            print "hubo error"
            return -1
        if not (len(s1 ) > 0) : return 0
        return s1

#######################################################################
    def termina(self,pids):
        #verificar si esta corriendo y terminarlo
        print 'pids',pids

        if pids!=[]:
            print "Terminating PIDS ",pids
            for id in pids:
                print 'id',id
                cmd = "kill -9 "+id
                print cmd
                rx=self.ejecuta(cmd)
                print rx


#######################################################################
    def checa_proceso(self,programa):
        print "checando proceso de programa",programa
        cmd = "pgrep -l -f \"%s\"" % (programa)
        #print cmd
        rx = self.ejecuta(cmd)
        #print 'rx',rx
        # quitar /n
        # V1.3
        proceso = []

        tipo = str(type(rx))
        if tipo.find("str") > 0:
            # print "si es string"
            rx = rx.strip()
            # verificar si en lista esta el propio pgrep
            rx = rx.split("\n")
            #print '--->',rx

            for a in rx:
                print "Procesando renglon=",a
                if 'pgrep' in a:
                    print "se autodetecto pgrep, removing....."
                elif Myname in a:
                    print "se autodetecto este mismo programa"
                else:
                    num = len(a)
                    if num > 0:
                        id = a.split()
                        id = id[0]
                        print "anexando proceso=" ,id
                        proceso.append(id)
        else:
            proceso = []
        print "proceso",proceso
        return proceso
#######################################################################
print 40*'-'
arg = string.join(sys.argv[1:])
Myname=sys.argv[0]
Myname=Myname.strip("./")
print 'Running:',Myname

x = UNLOAD()
w=x.checa_proceso(arg)
x.termina(w)
print 40*'-'