# -*- coding: utf-8 -*-
from pylab import *
import numpy
from numpy import polyfit ,poly1d

import pyfits
from pylab import *
from scipy import average, std, median, random, zeros, clip, array, append, mean
from scipy import histogram, optimize, sqrt, pi, exp, where, split
from scipy import sum, std, resize, size, isnan
from scipy import ndimage
from scipy import loadtxt, savetxt
from math import log

import os.path
from os import listdir
import matplotlib.pyplot as plt

import c_bin2fits
from c_bin2fits import *

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# V0.2, E. Colorado -Mar-2013- Update, para tambien usar stand alone sin gui
############################################################################
class ANALISIS():

    imagenes_mean=[]    #vector de promedios de los set
    imagenes_var=[]    #vector de varianza/2 de los set
    bias_mean=0
    bias_var=0

    #de todas las imagenes
    all_img_mean=[]
    set_img_mean0=[]
    set_img_mean1=[]
    set_img_mean2=[]

    eruido=0
    idstd=0

    bias_list=[]
    images_list=[]
    set_images_list=[]
    lista_tiempo=[]

############################################################################
    def __init__(self):
        print "Clase Analisis "
        self.X1=self.Y1=500
        self.X2=self.Y2=600
        self.B=c_bin2fits.BIN2FITS()
        self.id='>Marconi3 Left'
        self.full_well=150000
        self.pdf_dir='/imagenes'

##############################################################
    def load_fit(self,f_imagen):
        print "load_fit:",f_imagen
        hdulist = pyfits.open(f_imagen)
        image_data = hdulist[0].data
        hdulist.close()

        n=image_data
        print "=========================="
        print "dim",n.ndim
        print "shape",n.shape
        print "type",n.dtype
        print "itemsize",n.itemsize
        print "=========================="
        return image_data
##############################################################
    def save_fit(self,f_imagen,data):
        print "saving to fits",f_imagen
        hdu = pyfits.PrimaryHDU(data)
        hdu.writeto(f_imagen)

##############################################################
    #OJO: los ejes estan volteados en las matrices
    #X=Cols, se definen al final
    #CCD=cols x Rows
    #numpy= Rows x Cols
    def get_sub_image(self,f_imagen):
        x1=int(self.Y1)
        x2=int(self.Y2)
        y1=int(self.X1)
        y2=int(self.X2)
        hdulist = pyfits.open(f_imagen)
        image_data = hdulist[0].data
        hdulist.close()

        print "sacando sub imagen y=%d:%d, x=%d:%d"%(x1,x2,y1,y2)
        print 'shape',image_data.shape

        sub_image_data=image_data[x1:x2,y1:y2]
        return sub_image_data
##############################################################
    def estadistica(self,data):
        imean=abs(average(data))
        print 'Mean=',imean,
        istd=std(data)
        print 'Std=',istd,
        ivariance=ndimage.variance(data)
        print 'Variance=',ivariance

        return imean,istd,ivariance
##############################################################
    def calculo_bias(self,bias_list):
        print '\n Calculando Bias...'
        bmean=[]
        bstd=[]
        bvariance=[]

        for bias_file in bias_list:
            print 'procesando bias',bias_file,
            ib1=self.get_sub_image(bias_file)
            imean,istd,ivariance=self.estadistica(ib1)
            bmean.append(imean)
            bstd.append(istd)
            bvariance.append(ivariance)

        print "BIAS---------------------------------------------"
        self.bias_mean=average(bmean)
        print 'avg mean=',self.bias_mean,

        self.bias_var=average(bvariance)
        print 'variance=',self.bias_var
        print 'Bias End \n'
##############################################################
    def calculo_media(self,imagenes_list):
        print '\nCalculando media de los set de imagenes'

        for imagenes in imagenes_list:
            #variables temporales para sets de 3
            bmean=[]
            bstd=[]
            bvariance=[]
            print imagenes
            conta=0
            for set in imagenes:
                #print 'set=',set
                print 'procesando imagen',set,
                data=self.get_sub_image(set)
                imean,istd,ivariance=self.estadistica(data)
                bmean.append(imean)
                bstd.append(istd)
                bvariance.append(ivariance)
                #Datos individuales
                self.all_img_mean.append(imean)
                if conta==0:
                    self.set_img_mean0.append(imean)
                elif conta==1:
                    self.set_img_mean1.append(imean)
                elif conta==2:
                    self.set_img_mean2.append(imean)
                else:
                    print "ERROR, contador fuera de rango"

                conta+=1


            print "Ya procese grupo.............................."
            self.set_mean=average(bmean)
            print 'avg mean',self.set_mean
            #promedio de las 3 imagenes
            self.imagenes_mean.append(self.set_mean)

        print 'media End \n'
##############################################################
    def calculo_varianza_resta(self,imagenes_list):
        print '\nCalculando varianza  de las resta de imagenes'

        for imagenes in imagenes_list:
            #variables temporales para sets de 3

            bvariance=[]
            print 'Procesando set de imagenes',imagenes
            data0=self.get_sub_image(imagenes[0])
            data1=self.get_sub_image(imagenes[1])
            data2=self.get_sub_image(imagenes[2])

            #restas
            r=data0-data1
            imean,istd,ivariance=self.estadistica(r)
            bvariance.append(ivariance/2)

            r=data0-data2
            imean,istd,ivariance=self.estadistica(r)
            bvariance.append(ivariance/2)

            r=data1-data2
            imean,istd,ivariance=self.estadistica(r)
            bvariance.append(ivariance/2)


            print "Ya procese grupo.............................."

            set_var=average(bvariance)
            print 'variance',set_var
            self.imagenes_var.append(set_var)

##############################################################
    def calculo_final(self):
        print "------------------------------------------------------"
        txt=''
        gain=[]
        conta=0
        #calcular vector de ganancias
        for s in self.imagenes_mean:
            g=(s-self.bias_mean)/(self.imagenes_var[conta]-self.bias_var)
            gain.append(g)
            print 'Gain %d = %3.2f'%(conta,g)
            conta+=1

        '''
        print "Gain promedio=",average(gain)," e-/ADU"
        self.idstd=sqrt(self.bias_var)
        print 'Desviacion estandar del CCD=',self.idstd," ADU"
        #self.eruido=sqrt(self.bias_var)*gain[0]
        self.eruido=sqrt(self.bias_var)*average(gain)
        print 'Ruido e-=',self.eruido
        print 'Rango Dinamico=',65000/self.idstd
        print 'Bits Efectivos',log2(self.full_well/self.eruido)
        '''
        txt= "Gain promedio="+str(average(gain))+" e-/ADU\n"
        self.idstd=sqrt(self.bias_var)
        txt+= 'Desviacion estandar del CCD='+str(self.idstd)+" ADU\n"
        #self.eruido=sqrt(self.bias_var)*gain[0]
        self.eruido=sqrt(self.bias_var)*average(gain)
        txt+= 'Ruido e-='+str(self.eruido)
        txt+= '\nRango Dinamico='+str(65000/self.idstd)
        txt+= '\nBits Efectivos='+str(log2(self.full_well/self.eruido))
        print txt
        #test
        #Ajustar polinomio
        '''
        z= polyfit(log10(self.imagenes_mean),log10(self.imagenes_var),1)
        print z
        m=z[0]
        print 'pendiente',m
        '''
        #graficar
        plt.figure(1)                # the first figure
        plt.subplot(111)
        plt.plot(self.imagenes_mean,self.imagenes_var,marker='+')
        #plt.loglog(imagenes_mean,imagenes_var)
        plt.ylabel('Varianza')
        plt.xlabel('Nivel de Senal')
        plt.yscale('log')
        plt.xscale('log')
        plt.title('Curva de Transferencia de Fotones '+self.id)
        plt.grid(True)
        plt.text(1000,3000,txt)
        #plt.text(1000,10000,'Hola')
        fig = plt.figure(1)
        canvas = FigureCanvas(fig)
        print "---->",self.pdf_dir
        mydir=str(self.pdf_dir+"/PTC.pdf")
        print mydir
        canvas.print_figure(mydir, dpi=144)

##############################################################
    def calculo_quantum(self):
        file_list=loadtxt("monocromador/monocromador.txt",dtype='S16')
        lista_lamda=range(4000,9250,250)    #4000 a 9000

        bmean=[]
        for file in file_list:
            print 'procesando file',file
            ib1=self.get_sub_image('monocromador/'+file)
            imean,istd,ivariance=self.estadistica(ib1)
            bmean.append(imean)

        #normalizar Resultados
        #print 'media maxima', max(bmean)
        bmean=bmean/(max(bmean)/95.0)

        #graficar
        plt.figure(3)
        plt.subplot(111)
        plt.plot(lista_lamda,bmean)
        plt.title('Eficiancia Cuantica '+self.id)
        plt.ylabel('Eficiencia Cuantica Porcentual (%)')
        plt.xlabel('Longitud de onda (Angstroms)')
        #plt.yscale('log')
        #plt.xscale('log')
        plt.grid(True)
##############################################################
    def calculo_linealidad(self):
        file_list=loadtxt("linealidad/lineal.txt",dtype='S16')
        lista_tiempo=range(1,len(file_list)+1,1)
        print "Numero de archivos a prosesar",len(file_list)

        bmean=[]
        for file in file_list:
            print 'procesando file',file,'<---------------------------'
            ib1=self.get_sub_image('linealidad/'+file)
            imean,istd,ivariance=self.estadistica(ib1)
            bmean.append(imean)

        #Ajustar polinomio
        z= polyfit(lista_tiempo,bmean,1)
        p=poly1d(z)
        #cacular los puntos teoricos con polinomio
        yy=[]
        error=[]
        conta=0
        for tiempo in lista_tiempo:
            yy.append(p(tiempo))
            e=p(tiempo)-bmean[conta]
            error.append(e)
            #print 'errores',p(tiempo),bmean[conta],e
            conta+=1
        print bmean[1]
        print yy[1]

        #graficar
        plt.figure(2)
        plt.subplot(111)
        #plt.plot(lista_tiempo,bmean,marker='+')
        plt.plot(lista_tiempo,bmean,'g^')
        plt.plot(lista_tiempo,yy,marker='1')

        plt.title('Linealidad'+self.id)
        plt.ylabel('Flujo Medio')
        plt.xlabel('Tiempo de Exposicion (seg)')
        #plt.yscale('log')
        #plt.xscale('log')
        plt.grid(True)

##############################################################
        #parecido al anterior, solo que este busca solo
        #los bloques de archivos
    def calculo_linealidad_dir(self):

        print "Calculo de la Linealidad por directorio ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        lista_tiempo=self.lista_tiempo
        bmean=self.imagenes_mean


        #Ajustar polinomio
        z= polyfit(lista_tiempo,bmean,1)
        p=poly1d(z)
        #cacular los puntos teoricos con polinomio
        yy=[]
        error=[]
        conta=0
        for tiempo in lista_tiempo:
            yy.append(p(tiempo))    #vector polinomio teorico
            e=p(tiempo)-bmean[conta]#Error
            error.append(e)         #vector de Error
            #print 'errores',p(tiempo),bmean[conta],e
            conta+=1
        print bmean[1]
        print yy[1]

        #exportar vector teorico
        self.p_teorico=yy
        self.error=error

        #nonlinearity
        #usando maximos errores segun photometrics
        linealidad=((max(error)+fabs(min(error)))/max(bmean))*100.0
        print "nonlinearity (%)",linealidad

        #graficar
        plt.figure(2)
        plt.subplot(111)
        plt.plot(lista_tiempo,bmean,marker='+') #promedios
        #Datos reales de los sets
        plt.plot(lista_tiempo,self.set_img_mean0,'g^')
        plt.plot(lista_tiempo,self.set_img_mean1,marker='x')
        plt.plot(lista_tiempo,self.set_img_mean2,marker='o')
        #teorico
        plt.plot(lista_tiempo,yy,'-')

        plt.title('Linealidad '+self.id)
        plt.ylabel('Flujo Medio')
        plt.xlabel('Tiempo de Exposicion (seg)')
        #plt.yscale('log')
        #plt.xscale('log')
        plt.grid(True)
        #plt.text(2,60000,'here is some text\nRedOne')
        fig = plt.figure(2)
        canvas = FigureCanvas(fig)
        canvas.print_figure(self.pdf_dir+"/linealidad.pdf", dpi=144)

        print "FIN Calculo de la Linealidad por directorio ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

##############################################################
    def calculo_linealidad_2(self):
        print 'Calculo Error de linealidad 2 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'


        lista_tiempo=self.lista_tiempo
        bmean=self.imagenes_mean
        #bmean=bmean1
        print len(lista_tiempo),len(bmean)

        #Ajustar polinomio
        z= polyfit(lista_tiempo,bmean,1)
        p=poly1d(z)
        #cacular los puntos teoricos con polinomio
        yy=[]
        error=[]
        rel=[]
        rel0=[]
        rel1=[]
        rel2=[]
        conta=0
        for tiempo in lista_tiempo:
            #vector punto teorico
            yy.append(p(tiempo))
            #error
            e=p(tiempo)-bmean[conta]
            error.append(e)
            #error porcentual
            r=(e/p(tiempo))*100.0
            rel.append(r)
            #hacer lo mismo para todos los puntos individuales
            #0
            e=p(tiempo)-self.set_img_mean0[conta]
            #error porcentual
            r=(e/p(tiempo))*100.0
            rel0.append(r)
            #1
            e=p(tiempo)-self.set_img_mean1[conta]
            #error porcentual
            r=(e/p(tiempo))*100.0
            rel1.append(r)
            #2
            e=p(tiempo)-self.set_img_mean2[conta]
            #error porcentual
            r=(e/p(tiempo))*100.0
            rel2.append(r)

            #print 'errores',p(tiempo),bmean[conta],e
            conta+=1
        print bmean[1]
        print yy[1]
        print error[1]
        print rel[1]

        print yy
        print bmean

        #nonlinearity
        linealidad=((max(error)+fabs(min(error)))/max(bmean))*100.0
        print "nonlinearity (%)",linealidad

        #graficar
        plt.figure(4)
        plt.subplot(111)
        #plt.plot(lista_tiempo,bmean,marker='+')
        plt.plot(bmean,rel,'--')
        plt.plot(self.set_img_mean0,rel0,'o')
        plt.plot(self.set_img_mean1,rel1,'v')
        plt.plot(self.set_img_mean2,rel2,'s')
        #plt.plot(lista_tiempo,yy,marker='1')

        plt.title('Error en Linealidad '+self.id)
        plt.ylabel('% de Error')
        plt.xlabel('Cuentas Promedio')
        #plt.yscale('log')
        #plt.xscale('log')
        plt.grid(True)
        #plt.text(2,60000,'here is some text\nRedOne')
        txt="nonlinearity (%%)=%3.3f"%linealidad
        print txt
        plt.text(1,0,txt)
        fig = plt.figure(4)
        canvas = FigureCanvas(fig)
        canvas.print_figure(self.pdf_dir+"/linealidad_error.pdf", dpi=144)
        self.error=error
        self.rel=rel
        self.linealidad=linealidad
        print 'Calculo Error de linealidad 2 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
##############################################################
    def calculo_linealidad_3(self):

        #estilo chava
        print "Calculo Linealidad 3, solo con 2 flats a media escala ^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        bias1=self.get_sub_image(self.bias_list[1])
        bias2=self.get_sub_image(self.bias_list[2])

        flat1=self.get_sub_image('/imagenes/SpecM3/ds9_023o.fits')
        flat2=self.get_sub_image('/imagenes/SpecM3/ds9_024o.fits')

        flatdiff=flat1-flat2
        biasdiff=bias1-bias2

        a=average(flat1)+average(flat2)-average(bias1)-average(bias2)
        b=std(flatdiff)**2-std(biasdiff)**2

        gain =a/b

        print "Linealidad metodo 3"
        print "Gain:",gain

        read_out_noise = gain * ndimage.variance(biasdiff) / sqrt(2)

        print "Readout Noise:",read_out_noise
        print "FIN Calculo Linealidad 3, solo con 2 flats a media escala ^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
##############################################################
    def show(self):
        #mostras las graficas
        plt.show()
##############################################################
    def set_roi(self,x1,x2,y1,y2):
        self.X1=x1
        self.X2=x2
        self.Y1=y1
        self.Y2=y2

        if not x2  >x1:
            print "Error eje X, revisa to ROI..........\n\n\n\n\n\n"
            self.X2=self.X1+50
        if not y2  >y1:
            print "Error eje Y, revisa to ROI..........\n\n\n\n\n\n"
            self.Y2=self.Y1+50
        print "New Roi  x=%d:%d, y=%d:%d"%(x1,x2,y1,y2)
##############################################################
    def busca_imagenes(self,work_dir):
        #busca todas las imagenes en un directorio y las clasifica
        # como bias o imagenes en sus listas


        bias_list=[]    #lista de Bias
        image_list = [] #Lista de imagenes

        im_list = listdir(work_dir)
        #im_list = sort(array(im_list)) #sort

        print "Directorio de trabajo :",work_dir
        print im_list

        for name in im_list:
            if name[0] != ".":
                if name[-6:] =='b.fits':
                    full = os.path.join(work_dir,name)
                    bias_list.append(full)
                elif name[-5:] =='.fits':
                    full = os.path.join(work_dir,name)
                    image_list.append(full)


        #ordenar listas
        self.images_list = sort(array(image_list))
        self.bias_list = sort(array(bias_list))


        print "Lista de Bias:",self.bias_list
        print '*************/n/n/n'
        #print self.images_list

        #hacer set de imagenes de 3
        n=len(self.images_list)/3
        print 'Vamos a hacer %d sets de 3'%n

        print self.set_images_list
        self.set_images_list=self.images_list.reshape(n,3)
        #self.set_images_list.shape=(30,3)
        print self.set_images_list


        #Sacar lista de tiempos
        for imagenes in self.set_images_list:
            print 'Procesando set de imagenes',imagenes
            #print imagenes[0]
            key=self.B.datos_keyword(imagenes[0],'EXPTIME')
            self.lista_tiempo.append(key.value)
##############################################################
    def conta_bits_img(self,f_imagen):
        #es tardada esta rutina
        #sacar la imagen
        hdulist = pyfits.open(f_imagen)
        image_data = hdulist[0].data
        hdulist.close()

        #image_data=image_data[1000:1200,1000:1200]


        #pasar la imagen 2d a 1d
        print image_data.shape
        image_data=image_data.flatten()
        print image_data.shape

        self.kk=image_data

        #matriz contador en zero
        sum=numpy.zeros(16)

        for numero in image_data:
            conta=0
            #print numero
            bits=numpy.binary_repr(numero,16)
            for b in bits:
                #print conta,'>',b
                sum[conta]+=int(b)
                conta+=1

        #poner primero LSB
        sum=sum[::-1]
        print 'r',sum

        #normalizar
        new=[]
        l=len(image_data)
        print "data len",l
        for x in sum:
            print x
            n=x/l
            new.append(n)

        print new
        #graficar
        plt.figure(5)
        plt.subplot(111)
        #configurar limitex eje x
        plt.xlim(0,15)
        plt.xticks(range(0,16))
        plt.ylim(-1.5,1.5)
        #plt.yticks([-1.2,-1,-.8,-.4,-.2,0,.2,.4,.8,1,1.2])
        #plt.plot(lista_tiempo,bmean,marker='+')
        plt.plot(range(0,16),new,'g^')
        plt.plot(range(0,16),new,marker='1')
        #plt.plot(lista_tiempo,yy,marker='1')

        plt.title('Frecuencia de Bits '+self.id)
        plt.ylabel('% uso')
        plt.xlabel('Bits')
        #plt.yscale('log')
        #plt.xscale('log')
        plt.grid(True)
        #plt.text(2,60000,'here is some text\nRedOne')


        fig = plt.figure(5)
        canvas = FigureCanvas(fig)
        canvas.print_figure(self.pdf_dir+"/bits.pdf", dpi=144)

##############################################################
    def show_tabla(self):
        print "info table"

        imagenes_list=self.set_images_list

        print imagenes_list

        conta_set=0
        i=0
        for imagenes in imagenes_list:
            #variables temporales para sets de 3
            #print imagenes
            conta=0
            for img in imagenes:
                print '(%d) set # %d -> %s'%(i,conta_set,img),
                print 'mean=',self.all_img_mean[i]

                conta+=1    #0 a 3
                i+=1        #total

            print 'Set t=%d, avg mean=%3.2f'%(self.lista_tiempo[conta_set],self.imagenes_mean[conta_set]),
            print 'esperado=%3.2f, error=%3.2f'%(self.p_teorico[conta_set],self.error[conta_set])

            conta_set+=1
##############################################################
    def centroide_from_data(self, data):
        #w,h = self.coordenadas(imagen)

        h,w=data.shape
        '''
        print "dim",data.ndim
        print "shape",data.shape
        print "tipo",data.dtype
        print "size",data.itemsize
        '''
        print "\nCalculando el Centroide............"
        hdudata = data
        imax=data.max()
        #imin=data.min()
        avg=average(data)

        flux,malos, SumaXZ, SumaYZ, SumaZ = 0, 0, 0, 0,0.0
        noise=(imax-avg)/2+avg
        if (noise >= imax): noise=avg
        print "avg",avg
        print "noise",noise
        for y in range(0,w):
                for x in range(0,h):
                        tmp = hdudata[x,y]
                        flux+=tmp
                        pix=tmp-noise
                        if (pix<0):
                                pix=0
                                malos+=1
                        SumaXZ+=x*pix;
                        SumaYZ+=y*pix;
                        SumaZ +=pix;
        Cx=SumaXZ/SumaZ
        Cy=SumaYZ/SumaZ
        buenos = w*h-malos
        self.flux=flux

        print "centroide %f,%f"%(Cy,Cx)
        print "pixeles ruidosos %d"%malos
        print "pixeles buenos %f"%buenos
        #print "pixeles max=%d, min=%d"%(imax,imin)

        return Cy, Cx, buenos, malos
##############################################################
'''
A=ANALISIS()

#overscan
#A.set_roi(2080,2100,100,120)
A.set_roi(1100,1200,850,950)

#A.id='>Marconi3 Left'
#A.busca_imagenes('/imagenes/marconi3/left')
A.id='>Marconi3 Right'
A.busca_imagenes('/imagenes/marconi3/right')

A.conta_bits_img('/imagenes/marconi3/right/right_0043o.fits')

A.calculo_bias(A.bias_list)
A.calculo_media(A.set_images_list)
#A.calculo_linealidad_dir()
A.calculo_linealidad_2()

#A.calculo_varianza_resta(A.set_images_list)
#A.calculo_final()

A.show()
'''


##############################################################
