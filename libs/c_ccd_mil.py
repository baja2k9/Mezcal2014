#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd
from c_ccd import *
from c_cliente import *
#import array
#import os
#import time


class CCD_MIL(CCD,CLIENTE):
    'Clase para uso del CCD mil de tona '
    def __init__(self):
        CCD.__init__(self)
        self.ip="132.248.243.7"
        #self.ip="localhost"
        self.puerto=9710
        self.num=0
        self.tam_binario=0
        self.xsize_total=1024
        self.ysize_total=1024
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.tipo="TH7896"
        self.label="Photometrics CCD"
        self.label2="CCD Mil"
	self.usuario="CCD Mil Tona class"
        self.can_readgain=True
        self.speed=45.45e-6
        self.termine=False
############################################################################3
    def get_temp(self):
        print "Con el thompson no se lee la temperatura"
############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT TH7896 ")
	
        data,status=self.manda("INIT TH7896 ")
        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")

############################################################################
    def expone(self):
        print "exponinendo para photo server V2.0 o superior............. "
        msec=self.etime*1000
        self.termine=False

        #ver si es dark o bias para manejar el shutter

        ccdmensaje="EXPONE ETIME=%d XSIZE=%d YSIZE=%d CBIN=%d RBIN=%d CORG=%d RORG=%d DARK=%d GAIN=%d LOOP=%d "\
        %(msec,\
        self.xsize*self.cbin, self.ysize*self.rbin,\
        self.cbin,self.rbin,\
        self.xorg,self.yorg,\
        not self.shutter,\
        self.gain,\
        self.n_frames)

        print ccdmensaje
        self.mis_variables.mensajes(ccdmensaje)
        #self.mis_variables.logging.debug(ccdmensaje)

        socket,status=self.manda_open(ccdmensaje)

        if status:
            socket.setblocking(1)
            #mando bien el mensaje
            #vamos a recibir datos
            self.lee_ccd(socket)
        else:
            self.mis_variables.mensajes(socket,"Log","rojo")
            self.stop=True
            print "No llego el mensaje de red"

        self.mis_variables.update_barra("done. ",0.001)

        #traer binario con mandabin cuando ya este listo los datos
        #self.trae_binario(self.tam_binario)
###########################################################################
###########################################################################
    def lee_ccd(self,socket):
        line=socket.makefile('r',1)	#manejo del socket tipo archivo
        while 1:
            if self.stop:					#verifica si se presiono Cancelar
                print "Lee_ccd Cancelado"
                break
            data=line.readline().strip()
            try:
                txt=str(data)
                ok=True
                #print txt
            except:
                ok=False
            if ok:
                print "rx=",data
                if len(data) >1:
					self.procesa_datos(data,socket)
            if not data:
                print "no mas datos...."
                break
            if data=="CLOSE":
                print "llego close"
                break

        print "lei todo red, termine"
        #cerrar todo
        line.close()
        socket.close()

############################################################################
    def procesa_datos(self,data,socket):

		binario=False
		mando=data.split()
		key=mando[0]
		#print "mando=",mando

		if key=="LEE_TEMP":
			self.mis_variables.update_temp(float(mando[1]))
			self.mis_variables.mensajes(data)

		elif key=="READING":
			self.mis_variables.update_barra(key,float(mando[1]))
			self.mis_variables.mensajes(data)

		elif key=="Estadistica":
			self.mis_variables.mensajes(data)

		elif key=="BINARIO":
			self.mis_variables.mensajes(data)
			#realmente manda pixeles
			binario=int(mando[1])
			self.tam_binario=binario*2
		elif key=='EXPONE_END':
			print 'Ya termine de exponer'
			self.termine=True
		return binario

############################################################################
    def trae_binario(self):
        tam=self.tam_binario
        print "en trae binario a sacar solo lo binario, bytes=%d",tam

        self.mis_variables.mensajes("MANDABIN Receiving %d Bytes"%(tam))

        socket,status=self.manda_open("MANDABIN ")
        if not status:
            print "No llego el mensaje de red"
            self.mis_variables.mensajes("Error red con MANDABIN > %s "%(status),"Log","rojo")
            self.stop=False
            return

        inicio= time.clock()
        self.bindata = ''
        while len(self.bindata) < tam:
            if self.stop:					#verifica si se presiono Cancelar
                print "Trae_binario Cancelado"
                break
            chunk = socket.recv(tam-len(self.bindata))
            #print "recibi chunk bytes,",len(chunk)
            if chunk == '':
                raise RuntimeError,\
                    "socket connection broken"
            self.bindata = self.bindata + chunk
            #print "van bytes,",len(msg)
        socket.close()
        final= time.clock()
        tiempo= final-inicio
        if tiempo==0: tiempo=0.01
        speed=tam/tiempo/1024.0
        texto="Network Speed %3.2f KBYTES x sec" %speed
        self.mis_variables.mensajes(texto)

        print "Recibi TOTAL bytes,",len(self.bindata)


        #grabar archivo binario
        '''if self.stop==False:					#verifica si se presiono Cancelar
            myfile = open('image.bin', 'wb')
            myfile.write(self.bindata)
            myfile.close()'''

        self.stop=False
############################################################################
    def espera_estatus(self,t):
		print "esperando ccd ",self.label2," ",t,"s.........."
		tini = time.time()
		#solo poner barra si el tiempo es >2 seg
		prog = 0
		t_read = (self.xsize*self.ysize)*self.speed
		tfinal=t+t_read
		print "tiempo final",tfinal, 'readout time=',t_read
		tactual=0
		told=0

		while tactual<tfinal :
			time.sleep(0.3)
			if self.stop:					#verifica si se presiono Cancelar
				print "Espera_estatus Cancelado"
				break
			if self.termine:
				print "ya termino la exposicion"
				break
			tactual = time.time()-tini				#t transcurrido
			if tactual > (told+1):
				told=tactual
				#print "tactual",tactual, ' t=',t
				#estamos en tiempo de lectura o de exposicion?
				if tactual <= t:
					#estamos exponiendo
					self.mis_variables.update_barraColor('blue')
					#prog = (tactual-t)*100/(tfinal)			#prog de tiempo para un ready
					prog=tactual*100.0/t
					mensaje="EXPOSE t = %.1fs de %.1fs "%(tactual,t)
					print mensaje
					self.mis_variables.update_barra(mensaje,prog)
				elif tactual > t:
					#estamos leyendo el ccd
					self.mis_variables.update_barraColor('red')
					prog = (tactual-t)*100/(t_read)			#prog de tiempo para un ready

					mensaje="READING CCD t = %.1fs de %.1fs "%(tactual-t,t_read)
					print mensaje
					self.mis_variables.update_barra(mensaje,prog)
				else:
					print "no se que esta pasando ???"

			while gtk.events_pending():
				gtk.main_iteration()

		print "Ya termine los tiempos, voy a checar los estados..."
		#verificar que ya este listo el ccd
		while True:
			time.sleep(2)
			if self.stop:					#verifica si se presiono Cancelar
				print "Espera_estatus Cancelado"
				break
			#self.set_timeout(5)
			data,status=self.manda("ESTADO ")
			#self.set_timeout(0)
			#time.sleep(0.3)
			if status:
				data = data.strip()
				if str(data) != "BUSY":
					print "Ya no esta BUSY",str(data)
					break
			while gtk.events_pending():
				gtk.main_iteration()


