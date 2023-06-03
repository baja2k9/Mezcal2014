#!/usr/bin/env python
# -*- coding: utf-8 -*-
#V0.1 Oct-2013, -E.Colorado inicio

'''
para debugear con ipython
recarga automatica del modulo
import ipy_autoreload
%autoreload 2
%aimport c_angular

dmesg:
pl2303 3-3.4:1.0: pl2303 converter detected
usb 3-3.4: pl2303 converter now attached to ttyUSB0

'''
import serial
import threading
import time

class POLIMA2_ANGULAR:
#------------------------------------------------------------------------------
    def __init__(self):
        print "Mesa Angular ready"
        self.DEBUG=True
        self.txt_callback=None
        self.__error=0.001
        self.angulo=-1

        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.bytesize = 8
        self.ser.parity = "N"
        self.ser.port = "/dev/ttyUSB0"
        self.ser.stopbits = 1
        self.ser.timeout = 1
        self.ser.xonxoff=True
        self.open()


#------------------------------------------------------------------------------
    def __del__(self):
        print "cerrando mesa angular de polima2"
        print "closed",self.ser.port
        self.ser.close()
        self.ser = None

#------------------------------------------------------------------------------
    def full_init(self ):
        print "Mesa Angular full init"
        #open ya
        #estado
        self.estado()
        if self.error==-1:
            self.estado()

        print "Estado", self.state_txt
        #home
        self.home()
        #esperar home
        ok=True
        while ok:
            time.sleep(1)
            self.estado()
            if self.state=="32" or self.state=="33":
                print "polarizador llego..."
                ok=0
                break



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    def open(self ):
        print "openning",self.ser.port
        self.ser.open()
        time.sleep(1)
#------------------------------------------------------------------------------
    def estado(self ):
        print "estado pol"
        self.ser.write("\r\n1TS\r\n")
        line = self.readline()
        #line=self.ser.read(10)
        print "rx=",line
        print "len",len(line)
        if len(line) ==0:
            print "Error al pedir estado mesa angular"
            self.error=-1
            self.state=-1
            return -1
        self.error=line[3:7]
        self.state=line[-2:]
        print "error",self.error
        print "state",self.state
        if self.state=='1E':
            self.state_txt="Homing"
        elif self.state=='28':
            self.state_txt="Moving"
        elif self.state=='32':
            self.state_txt="Ready from Homing"
        elif self.state=='33':
            self.state_txt="Ready from Moving"
        elif self.state=='0A':
            self.state_txt="NOT Referenced from RESET"
        else:
            self.state_txt="Unknown Error"

        print self.state_txt
        return line

#------------------------------------------------------------------------------
    def readline(self):
        #print "readline"
        return self.ser.readline().replace("\r", "").replace("\n", "")
#------------------------------------------------------------------------------
    def test(self ):
        self.open()
        self.estado()
        self.home()
        self.posicion_pol()
        self.mueve_pol(300,0)

#------------------------------------------------------------------------------
    def espera_pol(self,deseado):
        if self.DEBUG: print "esperando pol a",deseado
        a=deseado-self.__error
        b=deseado+self.__error

        print "movi polima a %f con errores posibles %f , %f"%(deseado,a,b)

        loop=1
        while loop:
            time.sleep(0.8)
            self.posicion_pol()
            if self.angulo==deseado: break
            if self.angulo >a and self.angulo<b:
                print "polima llego..."
                loop=0
                break
            else:
                print "polima no ha llegado , actual="+str(self.angulo)

#------------------------------------------------------------------------------
    def home(self ):
        print "Polarizador a HOME"
        self.ser.write("1OR\r\n")
#------------------------------------------------------------------------------
    def posicion_pol(self ):
        self.ser.write("1TP\r\n")
        line = self.readline()
        #line=self.ser.read(10)
        print "tx=",line
        print "len",len(line)
        #sacar solo la posicion
        #1TP233.54884
        if len(line) ==0:
            self.angulo=-1
            print "Error"
            return self.angulo

        self.angulo=float(line[3:])
        print "pos angular",self.angulo
        return self.angulo
#------------------------------------------------------------------------------
    def mueve_pol(self,angulo,auto=True):
        if self.DEBUG: print "moviendo polarizador a",angulo

        t="1PA%3.3f\r\n"% angulo
        self.ser.write(t)
        if auto:
            self.espera_pol(angulo)
        return True

