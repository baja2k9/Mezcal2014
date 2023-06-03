#!/usr/bin/env python
# -*- coding: utf-8 -*-
#https://www.lost-infinity.com/night-sky-image-processing-part-6-measuring-the-half-flux-diameter-hfd-of-a-star-a-simple-c-implementation/

from pylab import *
import numpy
from numpy import polyfit ,poly1d

import pyfits
from pylab import *
from scipy import average, std, median, array,append, mean
import array
from scipy import  sqrt,  split
from scipy import sum, std, resize, size
from scipy import ndimage


import os.path
from os import listdir
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from pyds9 import *
import time

############################################################################
def iround( fnumber):
    return int(round(fnumber))

############################################################################
class ENFOQUE():
    'Calculo de mejor FOCO usando HFD'

############################################################################
    def __init__(self):
        self.d = DS9()
        #self.d.set('zoom to fit')
        #self.d.set('scale log')
        self.radio=45

        self.images_list = []
        self.Main_list = []
        self.HFR_fits = []
        self.POS_fits = []

##############################################################
    def load_fit(self,f_imagen):
        print "load_fit:",f_imagen
        hdulist = pyfits.open(f_imagen)
        image_data = hdulist[0].data
        hdulist.close()

        n=image_data
        '''
        print "=========================="
        print "dim",n.ndim
        print "shape",n.shape
        print "type",n.dtype
        print "itemsize",n.itemsize
        print "=========================="
        '''
        return image_data
##############################################################
    def datos_keyword(self, imagen, keyword):
        # print "\nTodos los datos de: %s"%keyword
        hdufile = pyfits.open(imagen)
        hduhdr = hdufile[0].header

        if keyword == "ALL":
            print hduhdr
        else:
            k = hduhdr.get(keyword)
            key = pyfits.Card(keyword, k, '')  
        hdufile.close()
        return key
##############################################################
    def busca_imagenes(self,work_dir):
        #Busca en directorio
        im_list = self.images_list
        im_fits = []
        img_list = listdir(work_dir)

        print "El directorio de trabajo es:",work_dir
        #Ordena
        im_list=sort(img_list)

        for n in im_list:
            if n[-6:] == 'o.fits':
                Ft = os.path.join(work_dir,n)
                im_fits.append(Ft)
        return im_fits
##############################################################
    def enfoque(self):
        Directorio='David/Autofoco0/'

        self.Main_list=self.busca_imagenes(Directorio) #saca lista de imagenes
        #self.Main_list = ['David/Autofoco3/autofoco0021o.fits']

        print 'Lista HFR:  ', self.HFR_fits #lista cons los resultados de los radios
        self.POS_imagenes()
        print 'Lista Posiciones foco:  ', self.POS_fits #lista con las posiciones del secundario

        print '*'*50
        #manda a calcular todas la imagenes
        self.HFR_imagenes2()
        conta=0
        print 'lista  HFR'
        for h in self.HFR_fits:
            print h,self.Main_list[conta],self.POS_fits[conta]
            conta+=1


        plt.figure(1)
        plt.subplot(111)
        x,y,X21,Y1,X22,Y2=self.Mejor_foco()
        print 'Punto Mejor Foco: ',(x,y)
        plt.title("Mejor Foco")
        plt.xlabel("Posicion")
        plt.ylabel("HFR")
        #plt.plot(self.POS_fits,self.HFR_fits,marker='1', label="radios")
        plt.plot(self.POS_fits, self.HFR_fits, 'ro', label="radios")

        plt.plot(X21,Y1, marker='1', label="Y1 m_izq")
        plt.plot(X22,Y2, marker='1',label="Y2 m_der")

        plt.plot(x,y,marker='o',color='k', label="Best Focus")


        #mas
        pp=self.POS_fits
        hh=self.HFR_fits

        # Ajustar polinomio
        z = polyfit(pp, hh, 4)
        p = poly1d(z)
        hhh=[]
        for d in pp:
            hhh.append(p(d))

        #encontrar punto minimo de polimonio
        data=np.arange(min(self.POS_fits),max(self.POS_fits)+1,0.1)
        minimo=1e10
        for d in data:
            a=p(d)
            if a<minimo:
                minimo=a
                dx=d

        print 'valor minimo x polinomio', minimo, 'en',dx
        plt.plot(dx, minimo, marker='o', color='b', label="Best Focus 2 poly")
        plt.plot(pp, hhh, marker='1', label="poly-rad")


        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()
        Mejor_imagen=self.Encontrar_imagen(x)
        self.d.set_np2arr(Mejor_imagen)
##############################################################
    def Mejor_foco(self):
        #Recta 1
        L=int(len(self.POS_fits))
        L2=iround(L/2)  #mitad
        L3=iround(L2/2) #1/5
        print 'L',L,L2,L3

        X1=self.POS_fits[0:L2]
        Y1=self.HFR_fits[0:L2]
        print X1,Y1
        
        #Recta2
        X2=self.POS_fits[L2:L]
        Y2=self.HFR_fits[L2:L]

        #Ecuacion 1
        print X2,Y2
        Z1= polyfit(X1,Y1,1)
        p=poly1d(Z1)
        print 'Ec 1: ',p

        #Ecuacion 2
        Z2= polyfit(X2,Y2,1)
        p1=poly1d(Z2)
        print 'Ec 2: ',p1

        #Punto mejor foco
        x=(p1[0]-p[0])/(p[1]-p1[1])
        y=p[1]*x+p[0]

        Y1=Y1+[0]
        Y2=[0]+Y2
        X21=list(range(len(Y1)))
        X22=list(range(len(Y2)))
        #y=mx+b   x=(y-b)/m
        #Rectas para graficar sobre V
        for y1 in range(0,len(Y1)):
            X21[y1]=(Y1[y1]-p[0])/p[1]

        for y2 in range(0,len(Y2)):
            X22[y2]=(Y2[y2]-p1[0])/p1[1]

        return x,y,X21,Y1,X22,Y2
##############################################################
##############################################################
    def HFR_imagenes2(self):
        # manda a calcular los radios de todas las imagenes
        for img in self.Main_list:
            self.HFR_fits.append(self.HFR2(img))
##############################################################
    def POS_imagenes(self):
        #busca las posiciones de las imagenes
        for Img in self.Main_list:
            key = self.datos_keyword(Img, 'SECONDAR')
            self.POS_fits.append(key.value)
        return self.POS_fits
##############################################################
    def Buscar_Centroide(self,Im):
        #centroide con doble pasada
        c=ndimage.measurements.center_of_mass(Im)
        x1=x=iround(c[1])
        y1=y=iround(c[0])
        xr1=iround(y1-self.radio)
        xr2=iround(y1+self.radio)

        yr1=iround(x1-self.radio)
        yr2=iround(x1+self.radio)


        Im2 = Im[xr1:xr2, yr1:yr2]
        c = ndimage.measurements.center_of_mass(Im2)
        x = c[1]+yr1
        y = c[0]+xr1
        print 'Centroid ', (x, y)
        return x,y

##############################################################
    def Buscar_Centroide2(self, Im):
        # centroide con umbral

        ImCopy=numpy.copy(Im)
        imean = abs(average(ImCopy))
        print 'Mean=', imean,
        istd = std(ImCopy)
        print 'Std=', istd,
        ivariance = ndimage.variance(ImCopy)
        print 'Variance=', ivariance

        umbral = imean + 2 * istd
        print 'umbral', umbral

        ImCopy[ImCopy < umbral] = 0
        y,x = ndimage.measurements.center_of_mass(ImCopy)

        #ds9 comienza en 1 y numpy en 0
        x+=1
        y+=1
        print 'Centroid2 ', (x, y)
        return x, y
##############################################################
    def Buscar_Centroide3(self, Im):
        # centroide con umbral y doble pasada

        ImCopy=numpy.copy(Im)
        imean = abs(average(ImCopy))
        print 'Mean=', imean,
        istd = std(ImCopy)
        print 'Std=', istd,
        ivariance = ndimage.variance(ImCopy)
        print 'Variance=', ivariance

        umbral = imean + 2 * istd
        print 'umbral', umbral

        ImCopy[ImCopy < umbral] = 0

        y,x = ndimage.measurements.center_of_mass(ImCopy)

        # centroide con doble pasada, paso 2
        x1 = x
        y1 = y
        xr1 = iround(y1 - self.radio)
        xr2 = iround(y1 + self.radio)

        yr1 = iround(x1 - self.radio)
        yr2 = iround(x1 + self.radio)

        Im2 = Im[xr1:xr2, yr1:yr2]
        c = ndimage.measurements.center_of_mass(Im2)
        x = c[1] + yr1
        y = c[0] + xr1
        # ds9 comienza en 1 y numpy en 0
        x += 1
        y += 1
        print 'Centroid 3', (x, y)
        return x, y

        print 'Centroid3 ', (x, y)
        return x, y
##############################################################
##############################################################
    def HFR2(self, Imagen):
        print 'HFR2 -Half Focus Radio'
        f_img = Imagen
        img_orig = self.load_fit(f_img)
        m=numpy.copy(img_orig)

        #procesa imagen
        imean = abs(average(m))
        print 'Mean=', imean

        nx, ny = m.shape
        #print 'size m',m.size

        m=m.reshape(nx*ny,1)
        for d in range(nx*ny):
            if m[d]<imean:
                m[d]=0
            else:
                m[d] =m[d]-imean

        m = m.reshape(nx , ny)

        #x, y = self.Buscar_Centroide(m)
        #x, y = self.Buscar_Centroide2(img_orig)
        x, y = self.Buscar_Centroide3(img_orig)

        # Graficar radio
        cmd = "Circle (%d,%d,%d)" % (x, y, self.radio)
        # print cmd
        #mandar a DS9
        self.d.set_np2arr(img_orig)
        self.d.set('regions', cmd)

        #nuevo metodo
        #vector radios
        radios_lista=list(range(1,self.radio+1))
        #print 'radios',radios_lista

        flux=[]
        anterior=0
        for r in radios_lista:

            ff=self.cmask(x,y,r,m)
            #print 'flujo r',x,y,ff
            flux.append(ff)


        #print 'lista flux',flux
        #print len(flux)
        flux=sort(flux)
        #print flux
        flux_max=ff
        print 'flujo maximo',flux_max

        mid=flux_max/2.0
        print 'flujo medio',mid
        print 'flujo mean', mean(flux)
        print 'flujo median',median(flux)
        i=0
        for r in flux:
            #print 'r',r
            if r >mid:
                print 'encontre flujo medio en r=',i, 'flujo',r
                break
            i += 1

        #i=i-1
        #print 'i',i
        #print 'r',radios_lista[i]
        HFR=radios_lista[i]
        print 'aqui HFR',HFR
        ######
        H = mid * i / (r * 1.0)
        print '---> H', H
        ######
        '''
        plt.figure(1)
        plt.subplot(111)
        plt.plot(radios_lista,flux)
        plt.show()
        '''
        # Grafica HFR
        cmd = "circle(%d,%d,%d)" % (x, y, HFR)
        self.d.set('regions', cmd)


        #poner cruz
        s=30
        #/
        cmd = "line(%d,%d,%d,%d)" % (x-s, y-s, x+s,y+s)
        self.d.set('regions', cmd)
        #\
        cmd = "line(%d,%d,%d,%d)" % (x + s, y - s, x - s, y + s)
        self.d.set('regions', cmd)

        #time.sleep(1)
        HFR=H
        return HFR
##############################################################
    def Encontrar_imagen(self,Pos):
        print 'encontrando imagen cerca de pos',Pos
        print 'lista de focos',self.POS_fits
        print 'numero de imagenes',len(self.POS_fits)

        for i in range(0,len(self.POS_fits)-1):
            #print 'i',i
            if (self.POS_fits[i]>=Pos):
                print 'aqui',i,self.POS_fits[i]
                error1=self.POS_fits[i]-Pos
                error2=Pos-self.POS_fits[i-1]
                print 'error 1 y 2',error1,error2
                if (error1<error2):
                    Im=self.Main_list[i]
                else:
                    Im=self.Main_list[i-1]
                print 'Imagen con mejor enfoque: ', Im
                Im_matriz=self.load_fit(Im)
                break
        return Im_matriz
##############################################################
##############################################################
    def cmask(self,cx,cy, radius, array):
        Im=numpy.copy(array)
        #suma los valores dentro de un circulo
        #cx, cy centro del circulo
        #array es tipo numpy
        a, b = cy,cx
        nx, ny = Im.shape
        #print 'shape',nx,ny

        y, x = np.ogrid[-a:nx - a, -b:ny - b]
        #print 'x,y',y,x

        mask = x * x + y * y <= radius * radius
        #print 'mask',mask

        return (sum(Im[mask]))
##############################################################
##############################################################
#del dir imagenes, grafica de nasa
A=ENFOQUE()
A.enfoque()
##############################################################
