#!/usr/bin/env python
############################################################################
class CONFIGURA:
    tel="1.5m"
    host_marconi="192.168.0.38"
    puerto_arranque=6000
    weather_server="beta"
    weather_enable=1
    host_ccdphoto="192.168.0.39"
    host_ccdoan="192.168.0.204"

    def __init__(self):
        r=self.read_config()
        if r: self.info()
############################################################################
    def read_config(self):
        a="ccds.cfg"
        print "leyendo archivo de configuracion:",a
        try:	
            openfile = open(a, 'r')
        except:
            print "Error, no pude abrir ",a
            return False 
        
        str=openfile.read()
        openfile.close()
        t=str.split('\n')
        self.tel=t[0]
        self.host_marconi=t[1]
        self.puerto_arranque=int(t[2])
        self.weather_server=t[3]
        self.weather_enable=t[4]
        self.host_ccdphoto=t[5]
        self.host_ccdoan=t[6]
        
        return True
############################################################################
    def info(self):
        print "Telescopio:",self.tel
        print "PC Marconi:",self.host_marconi
        print "puerto_arranque:",self.puerto_arranque
        print "weather_server:",self.weather_server
        print "weather_enable:",self.weather_enable
        print "host_ccdphoto:",self.host_ccdphoto
        print "host_ccdoan:",self.host_ccdoan
    
############################################################################	
#a=CONFIGURA()
