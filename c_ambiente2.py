#!/usr/bin/env python
import os
############################################################################
class AMBIENTE:
    'Leer variables de ambiente de los parametros utilizados por el programa V2'
    #constructor
    def __init__(self,archivo=None):
        self.debug=True
        #for param in os.environ.keys():
        #	print "%20s %s" % (param,os.environ[param])

        #print "--------------------------------------"
        if archivo==None:
            self.archivo="/tmp/marconi.kk"
        else:
            self.archivo=archivo
            
        self.var={'CCD_FILTER_FILE':'ruca.fil','CCD_OBSERVER':'RedONE','CCD_INSTRUMENT':'x',\
        'CCD_BASE':'x','CCD_WDIR':'x','CCD_LAST':'x','CCD_CCD':'x','CCD_OBJECT':'x',\
        'CCD_BINN':'x',
        'CCD_XORG':'x','CCD_YORG':'y',
        'CCD_XSIZE':'x','CCD_YSIZE':'y',
        'CCD_MACRO':'None'
        }

        for d in self.var:
            r=self.lee_ambiente(d)
            self.var[d]=r
        if self.debug: self.info()
        #self.var['CCD_LAST']= 'sepa la bola'
############################################################################
    #destrucctor
    def __del__(self):
        self.salva_ambiente()
        class_name = self.__class__.__name__
        if self.debug: print class_name, "destroyed"

############################################################################
    def lee_ambiente(self,key):
        r=''
        try:
            r=os.environ[key]
        except:
            print "no encontre ",key
            return
        if self.debug: print "encontre ",key, "con valor ",r
        return r
############################################################################
    def salva_ambiente(self):
        #print "--------------------------------------"
        if self.debug: print "Generando archivo de ambiente:",self.archivo
        try:
            openfile = open(self.archivo, 'w')
        except:
            print "Error, no pude abrir ",a
            return False

        for d in self.var:
            self.var[d]
            str="export %s='%s'\n" % (d,self.var[d])
            #print str
            openfile.write(str)

        openfile.close()
############################################################################
    def info(self):
        print "-----------info---------------------------"
        print "Observer:",self.var['CCD_OBSERVER']
        print "Base Name:",self.var['CCD_BASE']
        print "Instrument:",self.var['CCD_INSTRUMENT']
        print "CCD:",self.var['CCD_CCD']
        print "Object:",self.var['CCD_OBJECT']
        print "Filter File:",self.var['CCD_FILTER_FILE']
        print "Work Dir:",self.var['CCD_WDIR']
        print "Last Image:",self.var['CCD_LAST']
        print "Last Macro:",self.var['CCD_MACRO']
        print "--------------------------------------"

############################################################################
#a=AMBIENTE()
