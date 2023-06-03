#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
class CONFIGURA:
    
    def __init__(self):
        
        #self.lista_wheel = [ "Clear", "Clear" ,  "Clear"  ,"Clear","RC"]
        #self.lista_rendijas = [ "70 microns", "150 microns" ,"Clear" ]
        #self.lista_filtros = [ "Ha 90A","OIII 60A", "SII 90A"  ,"Vacio" ]
        
        r=self.read_config()
        if r: self.info()
############################################################################
    def read_config(self):
        a="/home/observa/mezcal.cfg"
        print "leyendo archivo de configuracion:",a
        try:	
            openfile = open(a, 'r')
        except:
            print "Error, no pude abrir ",a
            return False 
        
        str=openfile.read()
        openfile.close()
        t=str.split('\n')
        #print t
        try:
            self.arma_lista(t)
        except:
            print 'Error en arma  lista'
            return False
        
        return True
############################################################################
    def arma_lista(self,t):
        self.lista_wheel=t[0:5]
        self.lista_rendijas=t[5:8]
        self.lista_filtros=t[8:12]
############################################################################
    def info(self):
        print 'lista wheel',self.lista_wheel
        print 'lista rendijas', self.lista_rendijas
        print 'lista filtros',self.lista_filtros
    
############################################################################	
#a=CONFIGURA()
#a.info()
