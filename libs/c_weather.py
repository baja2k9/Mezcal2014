#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import os
import urllib
import cStringIO
#import libxml2
import xml as libxml2
from time import sleep

# V0.1 E.colorado
#probada
#################################################################################################
class WEATHER():
      fecha="hoy"
      temp=22
      hum=55
      bar=700
      wind=12
      chill=""
      rain=""
      rain_rate=""
      heat=""
      dew=""
      weather_enable=False
      ok=0
      archivo="/imagenes/wxrss.xml"
      web="http://haro.astrossp.unam.mx/weather15/wxrss.xml"
      server='192.168.1.1'
      indirecto=True    #poner false si tienes acceso directo a haro
#################################################################################################
      def __init__(self):
            pass
#################################################################################################
      #quita lo inicial y final
      def Saca_valor(self,s):
	  s3=s.split(":")
	  #quitar <br>
	  x=s3[1]
	  l=len(x)
	  x=x[1:(l-5)]
	  return x

#################################################################################################
#aqui van los datos de las temp, etc solamente
      def procesaDatos(self,datos):
	s = datos.split("\n")
	#poner datos en lista
	l1 = list()
	for i in range( len(s) ):
	  if len(s[i] ) > 0 :
            l1.append( s[i])

	self.temp=self.Saca_valor(s[2])
	self.chill=self.Saca_valor(s[3])
	self.heat=self.Saca_valor(s[4])
	self.hum=self.Saca_valor(s[5])
	self.dew=self.Saca_valor(s[6])
	self.bar=self.Saca_valor(s[7])
	self.wind=self.Saca_valor(s[8])
	self.rain=self.Saca_valor(s[9])
	self.rain_rate=self.Saca_valor(s[10])


#################################################################################################
      #saca nada mas lo que queremos del xml
      def processNode(self,reader):
	#print "****************************************************************************"
	#print "Depth ",  reader.Depth(), " type ", reader.NodeType()," Name ",reader.Name(),"empty?", reader.IsEmptyElement(), "Valor=",reader.Value()
	if reader.Name()=="pubDate" and reader.NodeType()==1:
	  reader.Read()
	  self.fecha=reader.Value()
	if reader.Name()=="#cdata-section":
	  datos=reader.Value()
	  self.procesaDatos(datos)

#################################################################################################
      def weather_info(self):
	print "Fecha: ", self.fecha
	print "Temp:", self.temp
	print "Wind chill:", self.chill
	print "Heat Index:", self.heat
	print "Humedad:", self.hum
	print "Dew Point:", self.dew
	print "barometrics:", self.bar
	print "Wind:", self.wind
	print "Rain:", self.rain
	print "Data source:",self.web

#################################################################################################
      def get_weather(self):
        if self.indirecto:
            x=self.get_weather_indirecto()
            return x
	try:
		wb = urllib.urlopen(self.web)
	except:
                  print "no pude conectarme a:",self.web
                  #tratar metodo indirecto
                  x=self.get_weather_indirecto()
                  self.indirecto=True
                  return x

	input = libxml2.inputBuffer(wb)
	reader = input.newTextReader("REC")
	ret=reader.Read()

	while ret == 1:
		self.processNode(reader)
		ret = reader.Read()

    	if ret != 0:
        	print "%s : failed to parse" % (self.web)
		self.ok= 0
	else:
            print "--------------------"
	    self.ok=1

	return self.ok

#################################################################################################
#################################################################################################
      def get_weather_indirecto(self):
            print "weather indirecto"
            mando="hose %s 9777 --out echo update_weather "%self.server
            print mando
            rx=""
	    try:
		os.system(mando)
	    except:
                  print "algo fallo weather"
                  print rx
                  return 0


            sleep(0.3)
            os.system('sync')

            try:
			wb = urllib.urlopen(self.archivo)
	    except:
			print "Error, no pude abrir ",self.archivo
			return 0

            input = libxml2.inputBuffer(wb)
            reader = input.newTextReader("REC")
            ret=reader.Read()

            while ret == 1:
                    self.processNode(reader)
                    ret = reader.Read()

            if ret != 0:
                    print "%s : failed to parse" % (self.web)
                    self.ok= 0
            else:
                print "--------------------"
                self.ok=1

            return self.ok
#################################################################################################
'''
print "WEATHER CCD Ready.........."
a=WEATHER()
a.get_weather()
a.weather_info()
'''
