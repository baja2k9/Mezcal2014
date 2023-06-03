#!/usr/bin/env python
# -*- coding: utf-8 -*-

# V0.1 E. colorado 2010
# V0.2 E. Colorado, Sep-2011, se arreglo bug de ROI y anexo barra de tiempos de lectura y cancela
# V0.3 E. Colorado, Ene-2013, modificado para nueva electronica de Chava
# V0.4 E. Colorado, Feb-2013, modificado para leer binario con header
# V0.5 E. Colorado, Abril-2013, Verifico la conexion con en controlador al iniciar

import gtk
import c_ccd
from c_ccd import *
from c_cliente import *
import gtk

#import array
#import time
#import os

#Bin4 265 x 257
#bin3 354 x 342
#bin2 530 x 513
#bin1 1060 x 1026

class CCD_SITE4(CCD,CLIENTE):
    'Clase para uso del CCD site4 con electronica del OAN '
    def __init__(self):
        self.tam_binario=0
        CCD.__init__(self)
        self.tipo="site4"
        self.label="site4 (1k x 1k) Oan"
        self.label2="SI03"
        #self.xsize_total=1040
        #self.ysize_total=1026
        #2013
#fer        self.xsize_total=1060
#fer        self.ysize_total=1026
        self.xsize_total=1060
        self.ysize_total=1026
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.arscale=0.1423
        self.decscale=0.1423
        self.speed=70e3
        self.can_readtemp=False
        self.usuario="Site4 ccd class"
        self.ip="192.168.0.50"
        #self.ip="192.168.3.70"
        #self.ip="localhost"
        self.puerto=4950
        self.datatype='hybrid'     #ara sabir si ya es fits o no, binario con header
        self.extradata=14	   #header del chava de 14 bytes
        self.bin_n_roi=False	   #No se puede hacer ROI con Binning

############################################################################
    def inicializa(self):
        print "inicializando CCD",self.label
        self.mis_variables.mensajes("CCD INIT Site4 networked With OAN Electronics")
        ok=self.ping(self.ip,'Site4')
        if ok==0:
            #ok
            self.mis_variables.mensajes('Site4 Ping OK',"nolog","verde")

        else:
            self.mis_variables.mensajes('Site4 Ping BAD',"Log","rojo")


        s1,error=self.test_socket(self.ip,self.puerto,'Site4')
        print s1,error
        if error!=True:
            self.mis_variables.mensajes("BAD, Connection to Site4 Server App","Log",Color='red')
        else:
            self.mis_variables.mensajes("GOOD, Connection to Site4 Server App","Log",Color='green')

        '''
        data,status=self.manda("LIMPIA")

        if not status:
            print "bad"
            print data
            self.mis_variables.mensajes(data,"Log","rojo")
        '''
############################################################################
    def pre_expone(self):
        print "Pre-expone   TIPO:", self.imgtype
############################################################################
    def expone(self):
        print "exponinendo site4"
        milisec=int(self.etime*1000)
        #ver que tipo de exposicion es
        if self.cbin==1:
            #sera inagen completa?
            print "Valor de full_image: ", self.full_image
            if self.full_image==1:
                print "CCD imagen completa	TIPO:", self.imgtype
                if self.imgtype=='zero' or self.imgtype=='dark':
                    print "vamos hacer bias"
                    cmd="LIMPIA LIMPIA BIAS %d" % (milisec)
                else:
                    print "no es bias"
                    cmd="LIMPIA LIMPIA   OBS %d" % (milisec)
            else:
                print "CCD imagen estilo ROI 	TIPO:", self.imgtype
                #cmd="SI03_LIMPIA SI03_LIMPIA SI03_RDI %d %d %d %d %f" %(self.xorg, self.yorg, self.xsize, self.ysize, milisec)
		#Ocupamos los limites, no el tamano de la caja
		x2=self.xorg+self.xsize
		y2=self.yorg+self.ysize
		cmd="LIMPIA RDI   %d %d %d %d %d" %(self.xorg, self.yorg, x2, y2, milisec)
        else:
	    #imagen binniada
            if self.imgtype=='dark':
                print "Es un dark!"
                cmd="LIMPIA"
                #self.mis_variables.logging.debug(cmd)
                data,status=self.manda(cmd)
                self.mis_variables.mensajes(cmd)
                print "esperando %fs" %(self.etime)
                if self.etime < 4:
                    time.sleep(4)
                else:
                    time.sleep(self.etime)
                cmd="B-BINN %d %d" %(self.cbin,milisec)
            else:
                print "No es un Dark"
                cmd="LIMPIA LIMPIA BINN %d %d" %(self.cbin, milisec)

        print "Mandando comando----",cmd
        #self.mis_variables.logging.debug(cmd)
        data,status=self.manda(cmd)
        self.mis_variables.mensajes(cmd)
        print "Ya mande mando site del chava"



###########################################################################
    def espera_estatus(self,t):
        print "______________________________________________________________"
        print "Esperando ccd ",self.label2," ",t,"s.........."
        tini = time.time()
        prog = 0
        tfinal = (self.xsize*self.ysize)/self.speed
        #time.sleep(1)
        #tupdate=1	#mandar update cada segundo solamente
        tultimo=0
        enlectura=False
        CORRE=True

        print "tiempo final",tfinal
        while CORRE:
            if self.stop:					#verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
            tactual = time.time()-tini				#t transcurrido
	    #actualizar barra de tiempo si exp. es mayor a 3 segundos
	    if tactual > t+tfinal:
		    print "YA acabamos"
		    CORRE=False
	    if enlectura:
		#print "Estamos en en ciclo de lectura"
		#esto es ya el tiempo de lectura
		seg=tactual-tultimo
		#print "tactual=", tactual," seg=",seg, "tultimo=",tultimo
		#ya paso un segundo ?
		if seg >1:
			#ya paso un segundo
			tultimo=time.time()-tini
                	self.mis_variables.update_barraColor('red')
			prog = (tactual-t)*100/(tfinal)			#prog de tiempo para un ready
			mensaje="READING t = %.1fs de %.1fs "%(tactual-t,tfinal)
			print mensaje
			#print prog

                	self.mis_variables.update_barra(mensaje,prog)
			#tupdate=0
			tultimo=time.time()-tini
			#tupdate=tactual-tultimo
			#print "tupdate ",tupdate," tactual ",tactual, " tultimo ",tactual

	    else:
		    #print "Estamos en en ciclo de exposicion"
		    #Calcular tiempo transcurrido
		    seg=tactual-tultimo
		    #print "tactual=", tactual," seg=",seg, "tultimo=",tultimo
		    if seg >1:
			#ya paso un segundo
			tultimo=time.time()-tini
		    	self.mis_variables.update_barraColor('blue')
		    	prog = tactual*100/t
			#print prog
                    	mensaje="Acquiring t = %.1fs (Remainning %.1fs) de %.1fs "%(tactual,t-tactual,t)
		    	self.mis_variables.update_barra(mensaje,prog)
			print mensaje

		    #Terminamos tiempo de exposicion?
		    if tactual >= t: enlectura=True

            while gtk.events_pending():
                gtk.main_iteration()
	    time.sleep(0.1)
	print "sali ciclo prog"
        #self.mis_variables.update_barraColor('green')
	self.mis_variables.update_barra("Downloading...",100)
        while True:
            if self.stop:					#verifica si se presiono Cancelar
                print "Espera_estatus Cancelado"
                break
            data2,status=self.manda("??")
            print "llego",data2, " len",len(data2)
            if data2=='OK\n':
                print "llego Ok, ya esta listo"
                break
            time.sleep(0.1)
            while gtk.events_pending():
                gtk.main_iteration()
        self.mis_variables.update_barra("done.",0.001)
	print "Me tarde con la imagen --->",time.time()-tini
        print "termino site4 ____________________________________________"
        time.sleep(0.5)

############################################################################
    def trae_binario(self):
        #ojo cambio, faltaban 14 bytes
        self.tam_binario = self.xsize*self.ysize*2+self.extradata
        print self.tam_binario
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
            #print "pidiendo datos",tam-len(self.bindata)
            chunk = socket.recv(tam-len(self.bindata))
            #chunk = socket.recv(2)
            #print "recibi chunk bytes,",len(chunk)
            if chunk == '':
                raise RuntimeError,\
                    "socket connection broken"
            self.bindata = self.bindata + chunk
            #print "van bytes,",len(self.bindata),str(self.bindata)

        print "termine, caque los datos"
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
    def cancela(self):
	print " ^^^^^^^^^^^^^^^^ CANCELANDO CCD SITE4 ^^^^^^^^^^^^^^^^^^^"
	data,s=self.manda("CANCELA ")
        if not s:
            print "bad"
            self.mis_variables.mensajes(data,"Log","rojo")
        print "Si cancelamos CCD ",data

	#Ojo el hardware no quiere cancelar si estamos en lectura
	time.sleep(0.5)

	self.mis_variables.mensajes("Waiting for CCD....",None,"amarillo")
	#vamos a esperar que el CCD este listo para cualquier otra opcion
	contador=0
	error=False
	while True:
            data2,status=self.manda("??")
            #print "llego",data2, " len",len(data2)
            if data2=='OK\n':
                print "llego Ok, ya esta listo"
                break
	    if contador >10 and not error:
		    #solo ponerlo una vez
		    self.mis_variables.mensajes("Unable to Cancel, Hardware Did NOT Response! ->Maybe already reading?","Log","rojo")
		    error=True
		    self.mis_variables.mensajes("Waiting more for CCD....","Log","amarillo")
	    contador+=1
	    print "Contador=",contador, " Error=",error
            time.sleep(0.3)
	    if contador >200:
		    #espero que nunca llegue aqui
		    self.mis_variables.mensajes("Something BAD happened :)","Log","rojo")
		    break
            while gtk.events_pending():
                gtk.main_iteration()
	self.mis_variables.mensajes("CCD IS READY ...",None,"azul")
############################################################################
    def do_full_ccd(self):
        milisec=int(self.etime*1000)
        #sera bias ?
        print "imagen tipo:", self.imgtype
        if self.imgtype=='zero' or self.imgtype=='dark':
            print "vamos hacer bias"
            cmd="LIMPIA LIMPIA BIAS %d" % milisec
        else:
            print "no es bias"
            print self.imgtype
            cmd="LIMPIA LIMPIA OBS %d" % milisec

        self.mis_variables.logging.debug(cmd)
        data,status=self.manda(cmd)
        self.mis_variables.mensajes(cmd)
############################################################################
    def revisa_valores(self):
        #parecida a la de la clase principar, pero los numeros impares
        # se les suma uno
        #valor inicial no menor de 0
        if (self.xorg < 0):
            self.xorg=0

        if (self.yorg < 0):
            self.yorg=0

        #revisar origen en y no sea mayor al limite del ccd
        if (self.xorg >self.xsize_total):
            self.xorg=self.xsize_total-1

        if (self.yorg >self.ysize_total):
            self.yorg=self.ysize_total-1

        #revisar borde final
        if (self.xend > self.xsize_total or self.xend <1 ):
            self.xend=self.xsize_total

        if (self.yend > self.ysize_total or self.yend <1 ):
            self.yend=self.ysize_total

        if self.xorg+self.xsize > self.xsize_total:
            self.xsize = self.xsize - ((self.xorg + self.xsize) - self.xsize_total)
        if self.yorg+self.ysize > self.ysize_total:
            self.ysize = self.ysize - ((self.yorg + self.ysize) - self.ysize_total)

        #revisar tam. de ventana en x
        if (self.xsize>self.xsize_total or self.xsize<0):
            self.xsize=self.xsize_total
            print "aqui 1"

        if (self.ysize>self.ysize_total or self.ysize<0):
            self.ysize=self.ysize_total
            print "aqui 2"


        #verificar que las coordenadas sean pares
        #no se ocupa

        #verificar si es roi
        x=self.xsize_total==(self.xsize-self.xorg )
        y=self.ysize_total==(self.ysize-self.yorg )
        z=x and y
        #print "x= ",x," y= ",y," z= ",z
        self.full_image=z
        self.pixeles()

############################################################################
    def update(self):
	#el controlador del chava no es constante
	#Bin4 265 x 257
	#bin3 354 x 342
	#bin2 530 x 513
	#bin1 1060 x 1026

        self.xsize=self.xsize_total/self.cbin
        self.ysize=self.ysize_total/self.rbin

	if self.cbin==3:
	    self.xsize=354

	if self.cbin==4:
	    self.ysize=257



############################################################################
