#!/usr/bin/env python
# -*- coding: utf-8 -*-

#usa astrometry.net

#V0.1 E. Colorado, Dic-2015 -> Inicio a una semana de salir de vacaciones

#ej
#solve-field --overwrite --scale-units arcsecperpix --scale-low 0.46 --scale-high 0.48 --ra 248.9 --dec 9.7 --radius 0.5 PG1633_0990003o.fits
import os
import os.path
from subprocess import *
import sys
import pyfits
import string
import time

scale_error=5.0 #error de escala de placa en %
###########################################################
class ASTROMETRY():
    'Saca la astrometria de una imagen fits'


    def __init__(self):
       print "Class Astrometry.net"
       self.decscale=+0.2341 #tel84
       self.img_file=''
       #self.pgm='/usr/bin/solve-field'
       self.pgm='/usr/local/astrometry/bin/solve-field'
       self.params='--overwrite --no-fits2fits --no-verify --no-plots'
       self.output = 'No encontre Astrometria \n'
       self.is_solved = False
       self.radius = 0.5
###########################################################
    def RA_to_degrees(self,ra):
        r=ra.split(':')
        try:
            self.RA_DEG=int(r[0])*15+float(r[1])*15.0/60.0+float(r[2])*15.0/3600.0
        except:
            print "Error en conversion de RA a grados"
            self.RA_DEG=-1

        return self.RA_DEG
###########################################################
    def DEC_to_decimal(self,dec):
        r=dec.split(':')
        try:
            self.DEC_DEC=int(r[0])+float(r[1])/60.0+float(r[2])/3600.0
        except:
            print "Error en conversion de DEC a decimal"
            self.DAC_DEC=-1


        return self.DEC_DEC
###########################################################
    def datos_keyword(self,imagen, keyword):
        #print "\nTodos los datos de: %s"%keyword
        hdufile = pyfits.open(imagen)
        hduhdr = hdufile[0].header

        if keyword == "ALL":
            print hduhdr
        else:
            k=hduhdr.get(keyword)
            key = pyfits.Card(keyword, k, '')   #por compatibilidad de sofware viejo
        hdufile.close()
        return key
###########################################################
    def analisa_respuesta(self, x,wcs_file):
        #print "analisando --------------------------------------------------"
        x=x.split('\n')

        for linea in x:
            #print linea
            if linea.startswith('Field center: (RA H:M:S, Dec D:M:S)'):
                print linea
                centro=linea

        centro= centro.split('=')
        #print centro
        c=centro[1].strip(' (')
        #print c
        c=c.strip(').')
        #print 'c=',c
        ar=c.split(',')
        dec=ar[1].strip()
        ar=ar[0]
        #print ar
        #print dec

        #convertir a decimal
        a=ar.split(':')
        #print a
        self.centro_ar= abs(int(a[0]))+abs(int(a[1])/60.0)+abs(float(a[2])/3600.0)
        print 'Center ar=',self.centro_ar

        a=dec.split(':')
        #print a
        self.centro_dec= abs(int(a[0]))+abs(int(a[1])/60.0)+abs(float(a[2])/3600.0)
        print 'Center dec=',self.centro_dec





###########################################################

###########################################################

###########################################################
    def solve(self,img_file):
        self.img_file=img_file
        #sacar coordenadas
        ra=self.datos_keyword(self.img_file,'RA')
        dec=self.datos_keyword(self.img_file,'DEC')


        if len(ra.value) >0:
            print 'Imagen: AR:%s , DEC:%s'%(ra.value,dec.value)
            self.RA_to_degrees(ra.value)
            self.DEC_to_decimal(dec.value)
            coords_ok=True
        else:
            coords_ok=False
            print "La imagen no tiene coordenedas, no la voy a procesar"
            return False,0

        #sacar binning
        bbin=self.datos_keyword(self.img_file,'CCDSUM')
        b=bbin.value
        b=b.strip()
        b=b.split()
        b.sort()


        low=int(b[0])
        hi=int(b[1])
        #print low,hi
        low=self.decscale*low-self.decscale*low*scale_error/100.0

        hi= self.decscale*hi+self.decscale*hi*scale_error/100.0
        #print low,hi

        cmd='%s %s --scale-units arcsecperpix --scale-low %f --scale-high %f '\
            %(self.pgm,self.params,low,hi)

        if coords_ok:
            cmd2=' --ra %f --dec %f --radius 0.5 '%(self.RA_DEG,self.DEC_DEC)
            cmd+=cmd2

        cmd=cmd+' '+self.img_file
        print cmd
        inicio= time.clock()
        self.output=x=self.ejecuta(cmd)
        #x=self.ejecuta('ls')
        #print 'x=',x
        final= time.clock()
        tiempo= (final-inicio)*1000
        print "Tarde en resolver imagen  %f segundos"%tiempo

        #ver si se resolvio
        full_base=os.path.splitext(self.img_file)
        solve_file=full_base[0]+'.solved'
        #print solve_file
        self.is_solved= os.path.exists(solve_file)


        if self.is_solved:
            print "Si resolvimos la astrometria"
            self.analisa_respuesta(x,full_base[0]+'.wcs')
            ok=True
        else:
            print "Error, No encontramos astrometria"
            ok=False
        print "------------------------------------------------------------------------"
        self.ok = ok
        self.tiempo = tiempo

        return ok,tiempo
###########################################################
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

###########################################################
'''
a=ASTROMETRY()
s,t=a.solve('/home/colorado/CloudStation/Progs/PG1633_0990003o.fits')
print s,t
s,t=a.solve('/home/colorado/Downloads/cieloV_0001o.fits')
print s,t
s,t=a.solve('/imagenes/autofoco0014o.fits')
print s,t
s,t=a.solve('/imagenes/fli0013o.fits')
print s,t
'''