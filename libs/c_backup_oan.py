#!/usr/bin/env python
# -*- coding: utf-8 -*-
#formato II+AAMMDD+HHMMSS.fits
###########################################################
class BACKUP():
    'Manejo de los archivos de imagenes, backup para el OAN'
    
    def __init__(self):
        self.lista_tel=(None,'2.12m','1.5m','0.84m','1m','INAOE')
        #lista_instru=["Ruca","Mexman","Italiana","polarimetro","boller","Echelle","Polima2","Sbig_5_Filters","Sbig_10_Filters","sempol","otro"]
        self.dic_instru={"Ruca":"rc","Mexman":"mx","Italiana":"it","polarimetro":"p1","boller":"bc","Echelle":"ec",\
                         "Polima2":"po","Sbig_5_Filters":"s5","Sbig_10_Filters":"sx","sempol":"se","otro":"ot",\
        "Camila":"ca","Cid":"ci","Mezcal":"mz","Puma":"pu","Bolitas":"bo","Cuenta Pulsos":"cp",\
        "Danes":"da","Sophia":"so","EspectroPol":"es"}

###########################################################
    def genera_formato_backup(self,tel,instru,fechatiempo):
        #print tel
        #print instru
        #print fechatiempo
        
        
        try:
            num=self.lista_tel.index(tel)
        except:
            print "Error: No tengo declarado el telescopio:",tel
            num=0
            
        try:
            ii=self.dic_instru[instru]
        except:
            print "Error: No tengo declarado el instrumento:",instru
            ii='ot'
            
        #print num
        #print ii
        archivo=str(num)+ii+self.fechatiempo+".fits"
        
        #print 'archivo',archivo
        return archivo

###########################################################