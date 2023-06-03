#!/usr/bin/env python
# -*- coding: utf-8 -*-
#. E.Colorado V0.1 Oct-2013

'''
dmesg:
TDI USB Serial Device converter detected
[1357929.455151] usb 3-3.3: Detected FT232RL
[1357929.455154] usb 3-3.3: Number of endpoints 2
[1357929.455156] usb 3-3.3: Endpoint 1 MaxPacketSize 64
[1357929.455159] usb 3-3.3: Endpoint 2 MaxPacketSize 64
[1357929.455170] usb 3-3.3: Setting MaxPacketSize 64
[1357929.455542] usb 3-3.3: FTDI USB Serial Device converter now attached to ttyUSB1

'''
import serial
import threading
import time

class POLIMA2_LINEAL:
#------------------------------------------------------------------------------
    def __init__(self):
        print "Mesa Lineal ready"
        self.DEBUG=True

        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.bytesize = 8
        self.ser.parity = "N"
        self.ser.port = "/dev/ttyUSB1"
        self.ser.stopbits = 1
        self.ser.timeout = 1
        #self.ser.xonxoff=True
        self.open()
        self.mysleep=0.2
        self.terminal="\r\n"
        self.is_ready=False
        self.is_OUT_READY=False
        self.is_IN_READY=False



#------------------------------------------------------------------------------
    def __del__(self):
        self.stop()
        print "cerrando mesa lineal de polima2"
        print "closed",self.ser.port
        time.sleep(0.5)
        self.ser.close()
        self.ser = None
        self.is_ready=False
        self.is_OUT_READY=False
        self.is_IN_READY=False
#------------------------------------------------------------------------------
    def read_config(self):
        a="libs/home.mxt"
        print "leyendo archivo de configuracion:",a
        try:
            openfile = open(a, 'r')
        except:
            print "Error, no pude abrir ",a
            return False

        str=openfile.read()
        openfile.close()
        t=str.split('\n')
        #print t

        #ctrl-c
        self.ser.write('\x03')
        time.sleep(1)
        self.memory_clear()
        time.sleep(1)
        #download it
        for l in t:
            #print "tx:",l
            data=l+self.terminal
            self.ser.write(data)
            time.sleep(self.mysleep)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    def open(self ):
        print "openning",self.ser.port
        self.ser.open()
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    def readline(self):
        #print "readline"
        return self.ser.readline().replace("\r", "").replace("\n", "")
#------------------------------------------------------------------------------
    def test(self ):
        self.read_config()
        self.home()

        self.mueve_in()

        self.mueve_out()
        self.get_pos()

#------------------------------------------------------------------------------
    def memory_clear(self ):
        print "memory clear"
        self.ser.write("FD\r\n")
#------------------------------------------------------------------------------
    def home(self ):
        print "home"
        self.is_ready=False
        self.ser.write("EX 100"+self.terminal)
        time.sleep(self.mysleep)
        #wait for home
        while not self.is_ready:
            print "waiting for home"
            time.sleep(0.5)
        print "Home finded"

#-----------------------------------------------------------------------------
    def get_pos(self ):
        print "get pos"
        self.ser.write("PR P"+self.terminal)
        line = self.readline()
        #line=self.ser.read(10)
        print "tx=",line
        print "len",len(line)
        return line
#------------------------------------------------------------------------------
    def mueve_in(self):
        if self.DEBUG: print "moviendo meza lineal a pos. IN"
        #self.ser.write("MA 415000"+self.terminal)
        self.is_IN_READY=False
        self.ser.write("EX 200"+self.terminal)
        #wait for ready
        while not self.is_IN_READY:
            print "waiting for in_ready"
            time.sleep(0.5)
        print "in_ready finded"

#------------------------------------------------------------------------------
    def mueve_out(self):
        if self.DEBUG: print "moviendo meza lineal a pos. OUT"
        #self.ser.write("MA 120000"+self.terminal)
        self.is_OUT_READY=False
        self.ser.write("EX 300"+self.terminal)
        #wait for ready
        while not self.is_OUT_READY:
            print "waiting for OUT_ready"
            time.sleep(0.5)
        print "OUT_ready finded"
#------------------------------------------------------------------------------
    def start(self):
        self.alive = True

        self.monitoring_thread = threading.Thread(target = self.reader)
        self.monitoring_thread.setDaemon(1)
        self.monitoring_thread.start()
#------------------------------------------------------------------------------
    def stop(self):
        print "stop reader"
        self.alive = False
#------------------------------------------------------------------------------
    def reader(self):
        print "en serial reader"
        line = ""

        while self.alive:
            try:
                #print "paso 1"
                line = self.readline().replace("\r", "").replace("\n", "")
                #print "paso 2"
                if len(line) >0:
                    print line
                if line=="HOME_READY":
                    print "*****HOME_READY*****"
                    self.is_ready=True
                elif line=="IN_READY":
                    print "*****IN_READY*****"
                    self.is_IN_READY=True
                elif line=="OUT_READY":
                    print "*****OUT_READY*****"
                    self.is_OUT_READY=True



                # Validate checksum

                #print "ignorechecksum",self.ignorechecksum
            except:
                pass

        print "YA SALI de READER"
#------------------------------------------------------------------------------
    def full_init(self ):
        print "Mesa lineal full init"
        self.start() #rx serie
        self.read_config()
        self.home()

        #self.mueve_in()

        #self.mueve_out()
        #self.get_pos()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#l=LINEAL()
#l.full_init()
#time.sleep(10)
