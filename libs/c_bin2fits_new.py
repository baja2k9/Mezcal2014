#!/usr/bin/python
# -*- coding: utf-8 -*-
#import math
import pyfits
import numpy
import c_ccd
import c_sqm
import c_clima_local

from numpy import *

from c_ccd import *
#from c_astro import *
from c_telescopio import *
import time

# V0.1, E. Colorado, Inicio
# V0.2,Oct,2011, E.Colorado -> puse unos try para evitar errores y se grabe siempre le pre-header
# V0.3,Nov,2011, E.Colorado -> solo puse el calculo que se tarde hacer los headers
# V0.4,Feb,2012, E.Colorado -> cambie variable objeto a objetoid
# V0.5 Marzo,2012, E. Colorado -> cambie IMGTYPE por IMAGETYP
# V0.6 Mayo,2012, E. Colorado -> hice rutina para hacer upgrade a los fits de la sbig
# V0.6 Mayo,2012, E. Colorado -> Anexe lo de tona, cabie AH por HA
# V0.7 Feb,2013, E. Colorado -> Anexe lo del controlador nuevo de lamparas echelle y boller
# V1.7 Mar,2013, E. Colorado -> Datos leidos como uint16 ya no como int16, py fits hace la resta automatica
# V1.8 Mar,2013, E. Colorado -> Arregle  bug de libreria pyfits de ubuntu 12
# V1.9 Oct,2013, E. Colorado -> Puse EPOCH y utmiddle
# V1.91 Nov,2013, E. Colorado ->cambios para asegurar que sea 16 bits con ubuntu 12 y mas nuevos
# V1.92 Jul,2014, E. Colorado -> quite ccd gain
# V1.93 FILENAME
# V1.94 Ene-2015, E. Colorado -> Depuracion con Leo
# V1.95 May-2015, E. Colorado ->agrege lo de la nueva electronica de echelle
# V1.96 Mar-2016, E. Colorado ->cambios de header.update por header.set debido a actualizaciones de pyfits
# V1.97 Mar-2016, E. Colorado ->ut con microsegundos de resolucion, quite doble inicializacion de SQM
# V1.98 Dic-2017, E. Colorado ->Clima local con electronica de Edgar Cadena

#puse esta linea extra por error en cvs al migrar servidor
buffer = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x00\x01"

#class BIN2FITS(WEATHER,ASTRO,TELESCOPIO):
class BIN2FITS_MAIN(CCD):
    '''
    Clase para obtener estadisticas, minimos, maximos, centroides,
    sumarios, keywords y los valores de keywords de imagenes fits
    Tambien para crear imagen fits
    '''
    mi_ccd = c_ccd.CCD()
############################################################################
    def __init__(self):
        print "*** INIT ->USANDO BIN2FITS NUEVO *** "
        #verificar la version en uso
        ver=pyfits.__dict__['__version__']
        print "Version de pyfits:",ver
        if ver=='1.3':
            self.old_lib=True
        else:
            self.old_lib=False

        if ver=='2.4.0':
            print "Error, NO usar esta Version por Bug"
        print "pyfits old_lib?",self.old_lib
        self.pyfits_ver=ver
        self.k = []

        self.tel='2.12m'
        self.observerb2f='colorado'
        self.instrument='none'
        self.projectid=0

        self.epoca=2000
        self.airmass=1
        self.object = ''
        self.fit_coment = ''
        self.b2fitversion =  1.97
        self.fechatiempo='2012'    #para usarlo despues en archivo
        self.control_lamparas='None'     #apuntador clase lamparas
        self.sqm=c_sqm.SQM()
        self.clima=c_clima_local.CLIMA_LOCAL()


############################################################################
    def sumario(self,imagen):
        print "Mostrando el Sumario de "+imagen
        hdufile = pyfits.open(imagen)
        hdufile.info()
        hdufile.close()
############################################################################
    def coordenadas(self,imagen):
        print "\nBuscando Coordenadas..............."
        hdufile = pyfits.open(imagen)
        hduhdr = hdufile[0].header

        print "NAXIS1:", hduhdr['NAXIS1']
        hdux=hduhdr['NAXIS1']
        print "NAXIS2:", hduhdr['NAXIS2']
        hduy=hduhdr['NAXIS2']
        hdufile.close()

        return hdux,hduy
############################################################################
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
############################################################################
    def keywords(self, imagen):
        print "\nMostrando las Keywords............."
        hdufile = pyfits.open(imagen)
        hduhdr = hdufile[0].header
        #print hduhdr.ascardlist().keys()
        #obsoleto
        print 'obsoleto'
        hdufile.close()
############################################################################
    def estadistica(self, imagen):
        #w,h = self.coordenadas(imagen)
        print "\nEstadistica..........."
        hdudata = pyfits.getdata(imagen)

        min=hdudata.min()
        max=hdudata.max()
        mean=hdudata.mean()
        stdev = hdudata.std()


        print "El Minimo es %.0f"%min
        print "El Maximo es %.0f"%max
        print "La media es %f"%mean
        print "La Stdev es %f"%stdev

        return min,max,mean,stdev
############################################################################
    def estadistica_box(self, imagen):
        #w,h = self.coordenadas(imagen)
        print "\nEstadistica solo de 100x100..........."
        hdudata = pyfits.getdata(imagen)

        dx=100
        dy=100
        x=hdudata.shape[1]
        y=hdudata.shape[0]

        x1=x/2-dx/2
        x2=x/2+dx/2
        #print 'x=',x1,x2

        y1=y/2-dy/2
        y2=y/2+dy/2
        #print 'y=',y1,y2

        hdudata=hdudata[y1:y2,x1:x2]
        #print "new shape",hdudata.shape

        min=hdudata.min()
        max=hdudata.max()
        mean=hdudata.mean()
        stdev = hdudata.std()


        print "El Minimo es %.0f"%min
        print "El Maximo es %.0f"%max
        print "La media es %f"%mean
        print "La Stdev es %f"%stdev

        return min,max,mean,stdev
############################################################################
    def min_max2(self, imagen):
        #No usar es muy lenta!!!!
        w,h = self.coordenadas(imagen)
        print "\nMostrando la Estadistica..........."
        hdudata = pyfits.getdata(imagen)
        min, max, sum, sum2, stdev = 0, 0, 0, 0, 0
        for y in range(0,w):
            for x in range(0,h):
                tmp = hdudata[x,y]
                if tmp > max: max = tmp
                elif (tmp < min) or (min==0): min = tmp
                sum += tmp
                sum2+= tmp*tmp
        avg = sum/(w*h)

        print "El Minimo es %.0f"%min
        print "El Maximo es %.0f"%max
        print "\nAverage es %f"%avg
        if (sum <0 or sum2 <0):
            print "sum: %f, sum2:%f"%(sum,sum2)
        else:
            stdev = math.pow((sum2-(sum*sum)/(w*h))/((w*h -1)),0.5)
            print "Stdev es %f"%stdev

        return min,max,avg,stdev
############################################################################
    def centroide(self, imagen):
        w,h = self.coordenadas(imagen)
        print "\nCalculando el Centroide............"
        hdudata = pyfits.getdata(imagen)
        max=hdudata.max()
        avg=hdudata.mean()
        malos, SumaXZ, SumaYZ, SumaZ = 0, 0, 0, 0
        noise=(max-avg)/2+avg
        if (noise >= max): noise=avg
        print "avg",avg
        print "noise",noise
        for y in range(0,w):
                for x in range(0,h):
                        tmp = hdudata[x,y]
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
        print "centroide %f,%f"%(Cy,Cx)
        print "pixeles ruidosos %d"%malos
        print "pixeles buenos %f"%buenos

        return Cy, Cx, buenos, malos
############################################################################
    def creaFake(self, rango, x, y):
        n = numpy.arange(rango).reshape(x,y)
        hdu = pyfits.PrimaryHDU(n)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto('imagen-'+str(x)+'x'+str(y)+'.fits')
############################################################################
    def crear(self, datos, x, y, outfile):
        #ojo quitar
        #self.old_lib=True
        #print x,y,outfile
        #print 'old_lib',self.old_lib #es False


        cmd = "rm -f "+outfile
        os.system(cmd)
        if self.mi_ccd.datatype=='fits':
                print "seguramente los datos no estan en binario, ya son fits"
                cmd = "cp /imagenes/sbig.fits "+outfile
                os.system(cmd)
                print cmd
                #Vamos a hacer un upgrade al fits
                self.upgrade_fits_header(outfile)
                return

        if self.mi_ccd.datatype=='hybrid':
            print "Los datos estan en binario con Header"
            #leer header y quitar lo de los datos
            #header mide 14 bytes: "BIN 1024 1024\n"
            header=datos[0:13]  #sin el enter
            h=header.split()
            cols=int(h[1])
            rows=int(h[2])
            datos=datos[14:]
            print 'del header ',cols,' x ',rows
            #reajustar datos de la interfaz
            self.xsize=cols
            self.ysize=rows

        #el otro tipo de datos es 'raw'
        #print "si vamos a convertir a fits",x,y
        #print "tengo datos=",len(datos)
        #np = numpy.frombuffer(datos, dtype=numpy.uint16)
        #nota, original funciona con pyfits '1.3' y python 2.6
        #hay bug con version 2 y lo arreglan en la version 3.06




        np = numpy.frombuffer(datos, dtype=numpy.uint16)

        #print "min", min(np)
        #print "max",max(np)

        #np=np-32768
        #ojo las versiones iniciales no lo ocupaban el swap
        k=x
        x=y
        y=k

        #self.array_info(np)
        np.shape = (x,y)

        #header basico
        header= pyfits.Header()
        header.set("simple", "T", "Conforms to FITS standard")
        header.set("bitpix", 16, "array data type")
        #header.set('NAXIS1', x, "length of data axis 1")
        #header.set('NAXIS2', y, "length of data axis 2",after='NAXIS1')
        #print "fits: naxis1",x,"naxis2",y

        #header.set('BZERO', 32768, 'BZERO')
        #header.set('BSCALE', 1, 'BSCALE')
        #header.set('EXTEND', 'T')
        hdu = pyfits.PrimaryHDU(np,header)


        #Nuevo, por upgrade de librerias

        print "Escalando imagen con bscale y bzero para libs nuevas"
        #hdu.scale('int16','',bscale=1,bzero=32768)
        #hdu.scale('int16')

        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto(outfile)
        cmd = "cp "+outfile +" /imagenes/bak.fits"
        os.system(cmd)
        self.appendHeader(outfile,x,y)
        print 'Hice Fits nuevo:',outfile,x,y
############################################################################
    def appendHeader(self, image,x,y):
        print "guarda POST-header **********************************************"
        #print x,y
        inicio= time.clock()

        #hdufile = pyfits.open(image, mode='update',uint16=1)
        hdufile = pyfits.open(image, mode='update')
        hdr = hdufile[0].header

        key=hdr['BITPIX']
        #print key

        key=hdr['NAXIS1']
        #print 'NAXIS1',key

        key=hdr['NAXIS2']
        #print 'NAXIS2',key


        #hdr.set('NAXIS', 2)
        #hdr.set('NAXIS1', x, "length of data axis 1")
        #hdr.set('NAXIS2', y, "length of data axis 2",after='NAXIS1')
        hdr.set('BZERO', 32768, 'BZERO')
        #hdr.set('BSCALE', 1, 'BSCALE')


        for j in range(len(self.k)):
                hdr.set( self.k[j][0],self.k[j][1],self.k[j][2] )

        #print "gian",self.mi_ccd.gain
        #print "filter",self.mi_ccd.mi_filtro.filtro
        try:
                hdr.set("FILTER",self.mi_ccd.mi_filtro.filtro, "Filter", after = 'GAINMODE')
        except:
                hdr.set("FILTER",self.mi_ccd.mi_filtro.filtro, "Filter")

        if not self.mi_ccd.mi_filtro.angulo is None:
                hdr.set("POLANGLE",self.mi_ccd.mi_filtro.angulo, "Polarimetro angle", after = 'FILTER')
        else:
            print 'filtro angulo es None'

        if self.instrument=='Polima2' :
            #print "Si esta Polima2"
            hdr.set("POL2LIN",self.mi_ccd.mi_filtro.mesa_pos, "Polima2 Linear Position", after = 'FILTER')

        hdr.set("SECONDAR", self.mi_ccd.mi_secundario.foco,  self.m, after = 'ALTITUDE')
        #lo de la temp
        if self.mi_ccd.can_readtemp:
                hdr.set("CCDTEMP",self.mi_ccd.temp, "CCD temperarure (celsius degree)",after="EXPTIME")

        #lo extra
        if self.mi_ccd.extra_header:
                #print "si hay parametros extras del header"
                self.mi_ccd.update_extra_header()
                #hdr.set("CCDSIZE",self.mi_ccd.CCDSIZE, "Physical CCD Size")
                #hdr.set("DATASEC",self.mi_ccd.DATASEC, "CCD Virtual Section")
                #hdr.set("CCDSEC",self.mi_ccd.CCDSEC, "CCD Section")
                hdr.set("BIASSEC",self.mi_ccd.BIASSEC, "CCD BIAS Section")
                hdr.set("TRIMSEC",self.mi_ccd.TRIMSEC, "Data section containing usefuldata")
        else:
                print "No hay parametros extras del header"
        '''
        print "n_output actual",self.mi_ccd.n_output
        print "output ",self.mi_ccd.output
        print "output actual",self.mi_ccd.output_actual
        '''

        #numero de salidas
        #Ojo esto no aplica para FLI, lo modifico en su clase
        #self.mi_ccd.output[1]
        if self.mi_ccd.output_actual==0:
                n=1
        else:
                n=2

        #sera dual?
        if self.mi_ccd.output_actual==3:
                used=2
        else:
                used=1

        #hdr.set("NAMPS",n, 'Number of Amplifiers')
        #hdr.set("CCDNAMPS",used, 'Number of amplifiers used')
        hdr.set("AMPNAME",self.mi_ccd.lista_output[self.mi_ccd.output_actual][0], 'Amplifier name')

        #Voy a poner aqui los casos particulares, para sus clases
        self.mi_ccd.local_header(hdr)
        #################################

        hdr.set("FILENAME",image.split('/')[-1], "Original Host Filename")
        hdr.set("CREATOR","Python Oan ccds", "Name of the software task that created the file")
        hdr.set("VERSION",self.version, "Application Software Version")

        if self.fit_coment!='': hdr.add_comment(self.fit_coment,before='CREATOR')

        hdr.add_comment("FITS (Flexible Image Transport System) format is defined in 'Astronomy")
        hdr.add_comment("and Astrophysics', volume 376, page 359; bibcode: 2001A&A...376..359H", before='BZERO')
        hdr.add_comment("Visit our weather site http://www.astrossp.unam.mx/weather15", after ='VERSION')
        hdr.add_comment("for complete meteorological data of your observation night")

        #print 'bin2fits ver',self.b2fitversion
        try:
            hdr.add_history("bin2fits class V%3.2f"%self.b2fitversion)
        except:
            print 'no se pudo'
        hdr.add_history("Programmer: Enrique Colorado [ colorado@astro.unam.mx ]")
        hdr.add_history("Observatorio Astronomico Nacional -UNAM")
        hdr.add_history("V1.94 By E. Colorado & Leonel G. >Updated keywords names ")
        hdr.add_history("V1.7  By E. Colorado >Automatic Data type change uint16 to int16, pyfyts")
        hdr.add_history("V1.6  By E. Colorado >Change AH to HA, OAN Tonantzintla added")
        hdr.add_history("V1.1  By E. Colorado >Speed optimization")
        hdr.add_history("V1.00 By E. Colorado and Arturo Nunez >Ported to Python using pyfits")
        hdr.add_history("V0.50 By E. Colorado >Added interior mirrors temperatures")
        hdr.add_history("V0.49 By E. Colorado >Added BIASSEC parameter")
        hdr.add_history("V0.48 By E. Colorado >Aditional info for autofocus calculations")
        hdr.add_history("V0.4  By E. Colorado >Now we include timezone, and remove lat. sign")
        hdr.add_history("V0.3  By E. Colorado >Now we include weather data")
        hdr.add_history("V0.2  By E. Colorado >General OAN Working Release")

        #key=hdr['BITPIX']
        #print key

        hdufile.close()
        #tiempo
        final= time.clock()
        tiempo= final-inicio
        print "Tarde en post-header %f segundos"%tiempo
        #print "guarda post-header ENDED **********************************************"
############################################################################
    def guarda_header(self):
        #se ejecuta del main en un thread, es el pre-header
        print "Guarda Pre-header................................................"
        inicio= time.clock()

        geos200 = ["+31:02:39", "115:27:49", 2800]
        geos150 = ["+31:02:43", "115:28:00", 2790]
        geos84 = ["+31:02:42", "115:27:58",  2790]
        geostona = ["+19:01:55", "98:18:49",  2184]

        timezone=8
        self.k.append(["EXPTIME",self.mi_ccd.etime, "Integration Time, sec."])
        self.k.append(["DETECTOR",self.mi_ccd.tipo, "Internal Camera Name"])
        self.k.append(["CCDTYPE",self.mi_ccd.label2, "CCD Type"])

        self.k.append(["ORIGIN", "UNAM", "OAN SPM, IA-UNAM"])
        self.k.append(["OBSERVAT", "SPM", "Observatory"])

        #del gui
        s_tel = 0
        self.k.append(["TELESCOP",self.tel,"Telescope"])
        if self.tel == "2.12m":
                print "tengo el 2m, %s", geos200[0]
                s_tel=2
                self.k.append(["LATITUDE", geos200[0], "Latitude"])
                self.k.append(["LONGITUD", geos200[1], "Longitud"])
                self.k.append(["ALTITUDE", geos200[2], "Altitude"])
        elif self.tel == "1.5m":
                #print "tengo el 1.5m, %s", geos150[0]
                s_tel=1;
                self.k.append(["LATITUDE", geos150[0], "Latitude"])
                self.k.append(["LONGITUD", geos150[1], "Longitud"])
                self.k.append(["ALTITUDE", geos150[2], "Altitude"])
        elif self.tel == "0.84m":
                #print "tengo el 0.84m, %s", geos84[0]
                s_tel=0;
                self.k.append(["LATITUDE", geos84[0], "Latitude"])
                self.k.append(["LONGITUD", geos84[1], "Longitud"])
                self.k.append(["ALTITUDE", geos84[2], "Altitude"])
        elif self.tel == "1m":
                print "tengo el 1m, %s", geostona[0]
                s_tel=0;
                self.k.append(["LATITUDE", geostona[0], "Latitude"])
                self.k.append(["LONGITUD", geostona[1], "Longitud"])
                self.k.append(["ALTITUDE", geostona[2], "Altitude"])
                timezone=6

        else:
                print "Tengo el None (telescopio)"
                self.k.append(["LATITUDE", "None", "Latitude"])
                self.k.append(["LONGITUD", "None", "Longitud"])
                self.k.append(["ALTITUDE", "None", "Altitude"])
        self.m = ""
        if s_tel == 0: self.m = "Secondary Position (1 step = 5um)"
        elif s_tel == 1: self.m = "Secondary Position (1 steps = 10 um)"
        elif s_tel == 2: self.m = "F/ Secondary type"
        #self.k.append(["SECONDAR", self.foco,  m])

        self.k.append(["TIMEZONE", timezone, "Time Zone"])
        self.k.append(["OBSERVER",self.observerb2f, "Observer's Name"])
        self.k.append(["PROJ_ID",self.projectid, "Personal Project ID"])

        if self.objetoid.get_text()!="":
            self.k.append(["OBJECT", self.objetoid.get_text(), "Object"])
        else:
            self.k.append(["OBJECT","None", "Object"])

        self.k.append(["INSTRUME",self.instrument, "Instrument"])
        #version 0.7 boller y echelle
        if self.instrument=='boller' :
            print 'Estas usando las lamparas con el Boller '
            #pedir estado de lamparas y rendija
            try:
                self.control_lamparas.estado()
            except:
                print "No pude obtener estado de lamparas boller"

            self.k.append(["LAMP",self.control_lamparas.lamp_name, "Boller LAMP Status"])
            try:
                self.control_lamparas.Pide_posicion_rendija()
            except:
                print "No pude obtener posicion de rendija del boller"

            self.k.append(["SLIT",self.control_lamparas.posicion, "Boller Slit Position"])

        #********************
        #echelle 2015
        if self.instrument=='Echelle' :
            print 'Estas usando las lamparas con el Echelle '
            #pedir estado de lamparas y rendija
            try:
                self.control_lamparas.estado()
            except:
                print "No pude obtener estado de lamparas Echelle"

            self.k.append(["LAMP",self.control_lamparas.lampara, "Echelle Lamp Th-Ar Status"])

            self.k.append(["SLIT",self.control_lamparas.rendija, "Echelle Slit Position"])
        #********************
        #self.k.append(["GAINMODE",self.mi_ccd.gain, "Gain factor in the CCD"])
        #Los 2
        self.k.append(["IMGTYPE",self.imgtype, "Image Type"])
        self.k.append(["IMAGETYP",self.imgtype, "Image Type"])
        self.mi_ccd.epoca_actual()
        self.k.append(["EQUINOX",float(self.mi_ccd.epoca), "Equinox"])
        self.k.append(["EPOCH",float(self.mi_ccd.epoca), "Epoch same as Equinox"])

        #tiempo
        self.mi_ccd.dia_juliano()
        self.mi_ccd.calcula_ut_y_utmiddle(self.mi_ccd.etime) #incluye udate
        t=time.gmtime()
        self.k.append(["ST",self.mi_ccd.ts, "Sideral Time"])
        #self.mi_ccd.ut="%2.2d:%2.2d:%2.2d"%(t.tm_hour,t.tm_min,t.tm_sec)
        self.k.append(["ut",self.mi_ccd.ut, "Universal Time"])
        #poner utmiddle
        self.k.append(["utmiddle",self.mi_ccd.utmiddle, "UT for the middle of the observation"])
        self.k.append(["JD",self.mi_ccd.jd, "Julian Date"])
        #self.udate="%d-%2.2d-%2.2d"%(t.tm_year,t.tm_mon,t.tm_mday)
        self.k.append(["DATE-OBS",self.mi_ccd.udate, "Observation Date UTM"])
        #exportar fecha+tiempo para archivo de salida
        t=time.gmtime()
        self.fechatiempo='_%s_%2.2d:%2.2d:%2.2d'%(self.mi_ccd.udate,t.tm_hour,t.tm_min,t.tm_sec)

        # lo del CCD
        self.k.append(["CCDXBIN", self.mi_ccd.cbin, "Binning factor in x"])
        self.k.append(["CCDYBIN", self.mi_ccd.rbin, "Binning factor in y"])
        self.k.append(["CCDSUM", str(self.mi_ccd.cbin) + " " + str(self.mi_ccd.rbin), "Binning [ Cols:Rows ]"])

        #lo de la luna
        self.mi_ccd.compute_moon()
        self.k.append(["MOONPHAS", round(self.mi_ccd.moon_phase,3), "Moon Phase"])



        #coordenadas
        print "Voy a pedir coordenadas..."
        r=self.mi_ccd.mi_telescopio.lee_coordenadas()
        #luna
        if r and self.tel!="1m":
            # distancia a luna

            self.mi_ccd.dist_to_moon(self.mi_ccd.mi_telescopio.ar_dec, self.mi_ccd.mi_telescopio.dec_dec)
            self.k.append(["MOONSEP", round(self.mi_ccd.d2_moon, 2), "Moon Angular Separation Degrees"])
        else: print "no tona"
        
        if r:
                #print "si lei cordenadas"
                self.k.append(["RA",self.mi_ccd.mi_telescopio.ar,"Right Ascension"])
                self.k.append(["DEC",self.mi_ccd.mi_telescopio.dec, "Declination"])
                self.k.append(["HA",self.mi_ccd.mi_telescopio.ah, "Hour Angle"])
                airmass=self.masa_aire(15*self.mi_ccd.mi_telescopio.ah_dec,self.mi_ccd.mi_telescopio.dec_dec)
                self.mi_ccd.airmass=round(airmass,3)
                #poner solo 3 digitos
                self.k.append(["AIRMASS",self.mi_ccd.airmass, "Airmass"])
        else:
                print "no pude leer coords del tel"


        #temp murillito
        print "Voy a leer temp edificio"
        try:
                self.mi_ccd.mi_temp.lee_temp()
        except: print "Fallo temp interna"
        ##########################################################3
        #poner los datos de temperaturas internas
        self.k.append(["TMMIRROR",self.mi_ccd.mi_temp.t_primario, "Primary Mirror Temperature (celsius degree)"])
        self.k.append(["TSMIRROR",self.mi_ccd.mi_temp.t_secundario, "Secundary Mirror Temperature (celsius degree)"])
        self.k.append(["TAIR",self.mi_ccd.mi_temp.t_aire, "Internal Telescope Air Temperature (celsius deg"])

        #poner los datos meteorologicos
        print "Checar clima..."
        ok=self.mi_ccd.get_weather()
        if ok == 1:
                #print "vamos por el clima"
                self.mi_ccd.xtemp = self.mi_ccd.temp.split()
                self.mi_ccd.xtemp = self.mi_ccd.xtemp[0]
                self.k.append(["XTEMP",float(self.mi_ccd.xtemp), "Exterior Temperature (celsius degree)"])
                temp = self.mi_ccd.hum.split()
                self.k.append(["HUMIDITY",float(temp[0]), "% external Humidity"])
                temp = self.mi_ccd.bar.split()
                self.k.append(["ATMOSBAR",float(temp[0]), "Atmosferic Presure in mb"])
                self.k.append(["WIND",self.mi_ccd.wind, "Wind Direction"])
                self.k.append(["WDATE",self.mi_ccd.fecha, "Weather Acquisition Date (Now UTC time)"])
        else:
            print '**** ERROR NO puede actualizar datos del clima'

        utctime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(None))
        self.k.append(["DATE",utctime, "file creation date (YYYY-MM-DDThh:mm:ss UT)"])

        print "Pidiendo posicion secundario"
        try:
                self.mi_ccd.mi_secundario.pide_posicion()
        except: print "Fallo secundario"

        try:
            self.mi_ccd.mi_filtro.pide_posicion()
        except: print "Fallo filtros"
        try:
                self.mi_ccd.mi_filtro.posicion_pol()
        except: print "Fallo polarizador"

        #sqm
        print "Pidiendo datos SQM"
        if self.tel == "2.12m":
            if self.sqm.read():
                self.k.append(["SQM",self.sqm.mag, "Sky Brightness mag/arsec^2"])
            if self.clima.read():
                self.k.append(["I_TEMP", self.clima.temp, "Dome internal temperature"])
                self.k.append(["I_HUM", self.clima.hum, "Dome internal humidity"])
                self.k.append(["I_BAR", self.clima.presion, "Dome internal barometric sensor"])
                self.k.append(["LUX", self.clima.lux, "Dome internal lux sensor"])

        #tiempo
        final= time.clock()
        tiempo= final-inicio
        print "Tarde en pre-header %f segundos"%tiempo

        print "Guarda pre- header Ended ......................................................"

############################################################################
    def test(self):
        print "test"

        n = numpy.frombuffer(buffer, dtype=numpy.int16)

        print "dim",n.ndim
        print "shape",n.shape
        print n.dtype
        print n.itemsize
        print n
        n.shape = (3,2)
        print "=========================="
        print "dim",n.ndim
        print "shape",n.shape
        print n.dtype
        print n.itemsize
        print n

        np = n
        print "dim",np.ndim
        print "shape",np.shape
        print np.dtype
        print np.itemsize
        print np

        hdu = pyfits.PrimaryHDU(np)
        hdulist = pyfits.HDUList([hdu])
        outfile='aqui.fits'
        hdulist.writeto(outfile)
############################################################################
    def upgrade_fits_header(self,outfile):
        #lo uso para la sbig
        print 'upgrade_fits_header ',outfile
        print "-header **********************************************"
        inicio= time.clock()
        hdufile = pyfits.open(outfile, mode='update')
        hdr = hdufile[0].header

        #print len(self.k)
        for j in range(len(self.k)):
                hdr.set(self.k[j][0],self.k[j][1],self.k[j][2])

        #print "gian",self.mi_ccd.gain
        print "filter",self.mi_ccd.mi_filtro.filtro
        try:
                hdr.set("FILTER",self.mi_ccd.mi_filtro.filtro, "Filter", after = 'GAINMODE')
        except:
                hdr.set("FILTER",self.mi_ccd.mi_filtro.filtro, "Filter")

        if not self.mi_ccd.mi_filtro.angulo is None:
                hdr.set("POLANGLE",self.mi_ccd.mi_filtro.angulo, "Polarimetro angle", after = 'FILTER')

        if self.instrument=='Polima2' :
            print "Si esta Polima2"
            hdr.set("POL2LIN",self.mi_ccd.mi_filtro.mesa_pos, "Polima2 Linear Position")

        hdr.set("SECONDAR", self.mi_ccd.mi_secundario.foco,  self.m, after = 'ALTITUDE')
        #lo de la temp
        if self.mi_ccd.can_readtemp:
                hdr.set("CCDTEMP",self.mi_ccd.temp, "CCD temperarure (celsius degree)",after="EXPTIME")

        #lo extra
        if self.mi_ccd.extra_header:
                #print "si hay parametros extras del header"
                self.mi_ccd.update_extra_header()
                '''
                hdr.set("CCDSIZE",self.mi_ccd.CCDSIZE, "Physical CCD Size")
                #hdr.set("DATASEC",self.mi_ccd.DATASEC, "CCD Virtual Section")
                hdr.set("CCDSEC",self.mi_ccd.CCDSEC, "CCD Section")
                hdr.set("BIASSEC",self.mi_ccd.BIASSEC, "CCD BIAS Section")
                hdr.set("TRIMSEC",self.mi_ccd.TRIMSEC, "Data section containing usefuldata")
                '''
        else:
                print "No hay parametros extras del header"
        '''
        print "n_output actual",self.mi_ccd.n_output
        print "output ",self.mi_ccd.output
        print "output actual",self.mi_ccd.output_actual
        '''

        #numero de salidas
        #Ojo esto no aplica para FLI, lo modifico en su clase
        #self.mi_ccd.output[1]
        if self.mi_ccd.output_actual==0:
                n=1
        else:
                n=2

        #sera dual?
        if self.mi_ccd.output_actual==3:
                used=2
        else:
                used=1

        #hdr.set("NAMPS",n, 'Number of Amplifiers')
        #hdr.set("CCDNAMPS",used, 'Number of amplifiers used')
        hdr.set("AMPNAME",self.mi_ccd.lista_output[self.mi_ccd.output_actual][0], 'Amplifier name')

        #Voy a poner aqui los casos particulares, para sus clases
        self.mi_ccd.local_header(hdr)
        #################################


        hdr.set("CREATOR","Python Oan ccds", "Name of the software task that created the file")
        hdr.set("VERSION",self.version, "Application Software Version")

        if self.fit_coment!='': hdr.add_comment(self.fit_coment,before='CREATOR')
        hdr.add_comment("FITS (Flexible Image Transport System) format is defined in 'Astronomy", after ='EXTEND')
        hdr.add_comment("and Astrophysics', volume 376, page 359; bibcode: 2001A&A...376..359H", before='BZERO')
        hdr.add_comment("Visit our weather site http://www.astrossp.unam.mx/weather15", after ='VERSION')
        hdr.add_comment("for complete meteorological data of your observation night")


        hdr.add_history("bin2fits class V%3.2f"%self.b2fitversion)
        hdr.add_history("Programmer: Enrique Colorado [ colorado@astro.unam.mx ]")
        hdr.add_history("Observatorio Astronomico Nacional -UNAM")
        hdr.add_history("V1.9  By E. Colorado >Now we include utmiddle")
        hdr.add_history("V1.7  By E. Colorado >Automatic Data type change uint16 to int16, pyfyts")
        hdr.add_history("V1.1  By E. Colorado >Speed optimization")
        hdr.add_history("V1.00 By E. Colorado and Arturo Nunez >Ported to Python using pyfits")
        hdr.add_history("V0.50 By E. Colorado >Added interior mirrors temperatures")
        hdr.add_history("V0.49 By E. Colorado >Added BIASSEC parameter")
        hdr.add_history("V0.48 By E. Colorado >Aditional info for autofocus calculations")
        hdr.add_history("V0.4  By E. Colorado >Now we include timezone, and remove lat. sign")
        hdr.add_history("V0.3  By E. Colorado >Now we include weather data")
        hdr.add_history("V0.2  By E. Colorado >General OAN Working Release")
        hdufile.close()
        #tiempo
        final= time.clock()
        tiempo= final-inicio

        print "Tarde en post-header %f segundos"%tiempo
        print "guarda post-header ENDED **********************************************"

############################################################################
    def array_info(self,n):
        print "=========================="
        print "dim",n.ndim
        print "shape",n.shape
        print "type",n.dtype
        print "itemsize",n.itemsize
        print "=========================="
############################################################################
    def myinfo(self):
        print "en clase nueva de bin2fits"
############################################################################
#f=BIN2FITS()
#f.test()
'''fits=PYF()
tam=sys.argv[1]
x=sys.argv[2]
y=sys.argv[3]
fits.crear(int(tam), int(x),int(y))
imagen = 'imagen-'+x+'x'+y+'.fits'
fits.sumario(imagen)
fits.keywords(imagen)
fits.datos_keyword(imagen,"ALL")
fits.append(imagen)
fits.datos_keyword(imagen,"ALL")
min,max,avg,stdev = fits.min_max(imagen)
fits.centroide(imagen, avg)'''
