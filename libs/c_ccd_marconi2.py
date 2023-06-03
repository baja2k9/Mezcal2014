#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_ccd_esopo
from c_ccd_esopo import *

#2010, eco, funciona solo con servidor nuevo, marconiServer
#2016, ECO, CAmbie por default salida Left de lectura por falla del Right

class CCD_MARCONI2(CCD_ESOPO):
    'Clase para uso del CCD Marconi2 con electronica de Astronomical Researh Camera '
    def __init__(self):
        CCD.__init__(self)
        self.tipo="e2vm2"
        self.label="E2V (2k x 2k) Marconi2"
        self.label2="E2V-4240"
        self.xsize_total=2154
        self.ysize_total=2048
        self.xsize=self.xsize_total
        self.ysize=self.ysize_total
        self.xend=self.xsize_total
        self.yend=self.ysize_total
        self.arscale=0.2341
        self.decscale=0.2341
        self.rotate_axis=False

        self.usuario="Marconi2_ccd class"
        self.ip="192.168.0.40"
        self.puerto=9710
        self.gain=2.2
        self.read_noise=6.1

        self.output=2    #Num canales de salida
        self.n_output=2    #Num canales de salida
        self.default_output=1    #Num canales de salida
        self.output_actual=self.default_output

        self.INIT_COMMAND="INIT_MARCONI2 "
        self.INIT_MSG="CCD INIT_4240 Marconi2  from Astronomical research Cameras"

        #control de temperaturas
        self.temp=-110.0
        self.temp_hilimit=-105
        self.temp_lowlimit=-99.9
        self.can_readtemp=True

        self.extra_header=True
        self.data_cols=2048
        self.lista_data=[2048,2048,999,649,474]


############################################################################
    def update_extra_header(self):

        print "extra header del Marconi2"
        #considerad datos de overscan segun binning
        self.data_cols=self.lista_data[self.cbin]
        print "data cols",self.data_cols
        ###CCDSIZE
        '''
        The logical unbinned size of the CCD in section notation.  Normally
        this would be the physical size of the CCD unless drift scanning
        is done.  This is the full size even when subraster readouts are
        done.
        '''
        self.CCDSIZE="[1:%d,1:%d]"%(self.xsize_total,self.ysize_total)
        print "CCDSIZE",self.CCDSIZE


        ###DATASEC
        ini=1
        ##tenemos overscan final en la imagen?
        first_col=self.xorg+1
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            last_cols=self.xsize
        else:
            #last_cols=self.data_cols/self.cbin
            last_cols=self.data_cols-self.xorg
        self.DATASEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        print "DATASEC",self.DATASEC

        #self.DATASEC="[1:%d,1:%d]"%(self.xsize,self.ysize)
        #self.DATASEC="[%d:%d,%d:%d]"%(self.xorg+1,self.xsize,self.yorg+1,self.ysize)
        #print "DATASEC",self.DATASEC

        ###CCDSEC
        #es DATASEC sin binning
        '''
        The unbinned section of the logical CCD pixel raster covered by the
        amplifier readout in section notation.  The section must map directly
        to the specified data section through the binning and CCD to
        image coordiante transformation.  The image data section (DATASEC)
        is specified with the starting pixel less than the ending pixel.
        Thus the order of this section may be flipped depending on the
        coordinate transformation (which depends on how the CCD coordinate
        system is defined).
        '''
        #self.CCDSEC="[1:%d,1:%d]"%(self.xsize*self.cbin,self.ysize*self.rbin)
        self.CCDSEC="[%d:%d,%d:%d]"%(self.xorg*self.cbin+1,self.xsize*self.cbin,self.yorg*self.rbin+1,self.ysize*self.rbin)
        print "CCDSEC",self.CCDSEC


        ###BIASSEC
        '''
        Section of the recorded image containing overscan or prescan data.  This
        will be in binned pixels if binning is done.  Multiple regions may be
        recorded and specified, such as both prescan and overscan, but the
        first section given by this parameter is likely to be the one used
        during calibration.
        '''
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            #no hay overscan
            self.BIASSEC='None'
        else:
            #first_col= (self.data_cols-self.xorg)/self.cbin+1
            first_col= (self.data_cols-self.xorg)+1
            if first_col <1: first_col=1
            self.BIASSEC="[%d:%d,1:%d]"%(first_col,self.xsize,self.ysize)
        print "BIASSEC",self.BIASSEC

        ###TRIMSEC
        #datos del CCD sin overscan, o sea lo restante de BIASSEC
        '''
        Section of the recorded image to be kept after calibration processing.
        This is generally the part of the data section containing useful
        data.  The section is in in binned pixels if binning is done.
        '''
        """
        first_col=self.xorg
        ini=(self.xsize_total-self.data_cols)/self.cbin+1
        #tenemos overscan inicial en la imagen?
        if first_col <ini:
            print "si hay overscan"
        else:
            ini=1
        """
        ini=1
        ##tenemos overscan final en la imagen?
        first_col=self.xorg+1
        r=self.xorg+self.xsize
        if r<=self.data_cols:
            last_cols=self.xsize
        else:
            #last_cols=self.data_cols/self.cbin
            last_cols=self.data_cols-self.xorg
        self.TRIMSEC="[%d:%d,1:%d]"%(ini,last_cols,self.ysize)
        print "TRIMSEC",self.TRIMSEC
############################################################################
print "Class CCD Marconi2 Ready.........."