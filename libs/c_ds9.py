import os
from subprocess import *
import time

#import commands

#V1.0, E.Colorado inicial
#V1.3, E.Colorado problema con pgrep por comportamiento diferente slackware y ubuntu
#ocupa xpa instalado y ds9
#V1.4 agrege restart iraf y ds9
#V1.5 agrege set_frame
#V1.6 Voy a correr todo desde bin/ds9
#V1.7 modificacioner para ubuntu 16.04 iraf direfente
#anexe line
############################################################################
class DS9:
    'manejo del ds9 con xpa access protocol'

    __ds9exe="./bin/ds9"	#quitarle ./ para que uso el ds9 del sistema
    def __init__(self,template="MarconiOnly"):
        self.template=template
        print "clase ds9 usando template",self.template
        self.restart_iraf_cmd="./xmarconids9iraf &"
############################################################################
    def getroi(self):
        cmd="./bin/xpaget "
        cmd +=self.template
        cmd +=" regions"
        #print cmd
        rx=self.ejecuta(cmd)
        return rx
############################################################################
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

        if not (len(s1 ) > 0) : return 0
        return s1
############################################################################
    #procesa roi solo tipo box
    #cual = el box deseado
    def roi(self,cual):
        #print 'roi',cual
        cx=cy=w=h=angulo=-1
        contador=0
        r=self.getroi()
        #print r
        #pasarlo a lista
        r = r.split("\n")
        l = list()
        for i in range(len(r)):
            if len(r[i] ) > 0 :
                l.append(r[i] )
                if (r[i].find("box")!=-1 ):
                    #print "encontre box"
                    contador+=1
                    if contador==cual :
                        #print "el el box que queremos"
                        a=r[i].lstrip('box(')
                        a=a.rstrip(')')
                        a=a.split(',');
                        #print a
                        cx=float(a[0])
                        cy=float(a[1])
                        w=float(a[2])
                        h=float(a[3])
                        angulo=float(a[4])
        #buscar en la lista
        return (cx,cy,w,h,angulo)
############################################################################
    def loadfile(self,archivo):
        cmd="./bin/xpaset "+"-p "+self.template+" file "+archivo
        print cmd
        self.ejecuta(cmd)

############################################################################
    def getfile(self):
        cmd="./bin/xpaget "+" "+self.template+" file "
        rx=self.ejecuta(cmd)
        return rx
############################################################################
    def do_init(self):
        print "sending DS9 initial parameters"
        cmd="./bin/xpaset "+" -p "+self.template+" regions shape box "
        self.ejecuta(cmd)
        #time.sleep(0.5)
        
        cmd="./bin/xpaset "+" -p "+self.template+" preserve pan yes "
        self.ejecuta(cmd)
        #time.sleep(0.5)
        
        cmd="./bin/xpaset "+" -p "+self.template+" zoom to fit"
        self.ejecuta(cmd)
############################################################################
    def circle(self, x,y,r):
        cmd = "echo \"circle %d %d %d \" | ./bin/xpaset %s regions" %(x,y,r,self.template)
        #print cmd
        self.ejecuta(cmd)
############################################################################
    def box(self, cx,cy,w=250,h=250):
        cmd = "echo \"box %d %d %d %d 0\" | ./bin/xpaset %s regions" %(cx,cy,w,h,self.template)
        #print cmd
        self.ejecuta(cmd)
############################################################################
    def run(self):
        #verificar si esta corriendo
        #version1.2, en algunos os se detecta asi mismo el pgrep, ya lo corregui
        #version1.3 funciona diferente el pgrep entre slackware y ubuntu

        print "running ds9",self.__ds9exe
        cmd="./bin/ds9 -mode region -title "+self.template
        print cmd
        proceso=self.checa_proceso(cmd)

        if proceso > 0:
            print "El id del ds9 es=",proceso
            print 'Ya no lo voy a volver a ejecutar'
        else:
            print "No esta corriendo"
            #vamos a correrlo
            cmd=self.__ds9exe +" -mode region -title "+self.template+ " &"
            print cmd
            os.system(cmd)
            return -1
############################################################################
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
        #print 'tipo',tipo
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
                elif 'sh' in a:
                        print "se autodetecto sh, removing....."
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
############################################################################
    def terminate(self):
        #verificar si esta corriendo y terminarlo
        print "Terminating ds9",self.__ds9exe
        cmd="pkill -f \"ds9 -title "+self.template+"\" &"
        print cmd
        rx=self.ejecuta(cmd)
        print rx


############################################################################
    def restart_iraf_ds9(self):
        #os.system('pwd')
        cmd="./unload2.tcl ds9 -mode region -title "+self.template
        rx=self.ejecuta(cmd)
        print rx

        cmd="./unload2.tcl start_iraf_observa.devmarconi0"
        rx=self.ejecuta(cmd)
        print rx

        #Para el nuevo iraf en ubuntu 16
        cmd= "./unload2.tcl /usr/local/bin/ds9 -fifo /home/observa/.devmarconi0/imt1 -title "+ self.template
        rx = self.ejecuta(cmd)
        print rx

        cmd = "./unload2.tcl /bin/csh -f /usr/local/instrumentacion/oan_ccds/umarconi"
        rx = self.ejecuta(cmd)
        print rx


        #volver a ejecutarlo
        cmd=self.restart_iraf_cmd
        rx=self.ejecuta(cmd)
        print rx

        time.sleep(5)
        self.do_init()

############################################################################
    def set_frame(self,frame):
        cmd="./bin/xpaset "+"-p "+self.template+" frame "+frame
        self.ejecuta(cmd)
############################################################################
    def set_mando(self,mando=None):
        cmd="./bin/xpaset "+"-p "+self.template+" "+mando
        print 'set_mando=',cmd
        self.ejecuta(cmd)

############################################################################
    def region_del(self ):
        cmd="./bin/xpaset "+" -p "+self.template+" regions delete all"
        self.ejecuta(cmd)


############################################################################
############################################################################
    def line(self, x1,y1,x2,y2):
        cmd = "echo \"line %d %d %d %d \" | ./bin/xpaset %s regions" %(x1,y1,x2,y2,self.template)
        #print cmd
        self.ejecuta(cmd)

############################################################################
