#!/usr/bin/env python
# -*- coding: utf-8 -*-
# E. colorado, convierte todo los archivos csv a pdf
# Le quite al mando el ./

#poner en crontab:
#01 00 * * * /usr/local/instrumentacion/oan_ccds/libs/search_csv_and_convert.py

import c_util
import sys
import os
from os import system, listdir
from scipy import  sort,array

util=c_util.UTIL()

log_dir='/imagenes/bitacora'
log_list = listdir(log_dir)
log_list=sort(array(log_list))
csv_list=[]
falta_list=[]


for name in log_list:
    print name
    fileName, fileExtension = os.path.splitext(name)
    #buscar solo los archivos csv
    if fileExtension =='.csv':
        csv_list.append(name)

#buscar a los archivos que no esten convertidos
for name in csv_list:
    fileName, fileExtension = os.path.splitext(name)
    filePdf=os.path.join(log_dir,fileName+'.pdf')
    print filePdf
    if os.path.isfile(filePdf):
        print 'El archivo '+filePdf+' Si existe'
    else:
        print 'El archivo '+filePdf+' No existe'
        falta_list.append(name)

#print 'Vamos a procesar los siguentes archivos :',falta_list
for name in falta_list:
    file=os.path.join(log_dir,name)
    print 'Convertiendo a PDF', file
    #ejecutar mando externo
    mando="csv2pdf.py "+file
    print mando
    resp=util.ejecuta(mando)
    print resp
