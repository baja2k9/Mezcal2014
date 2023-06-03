#!/usr/bin/env python
# -*- coding: utf-8 -*-

# V0.1 Ene-2012 -E. Colorado ->Inicio
# V0.2 Feb-2012 -E. Colorado ->Cambie tantito los colores de las columnas

import sys
import string
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch, mm
from reportlab.lib.pagesizes import A4, letter, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

global lista_comentarios, nc, ni
lista_comentarios=[]
########################################################################################

PAGE_WIDTH = 11 * inch
PAGE_HEIGHT = 8.5 * inch
################################################################################################
def process_csvfile2(filename):
    data =  []
    header=[]
    global lista_comentarios, nc, ni
    nc=0
    ni=0
    csvfile = csv.reader(open(filename))
    conta=1
    for row in csvfile:
        #print 'row->',row
        #newdata = [row[0],row[1]]
        if conta >4:
            #si es una imagen normal no perlarla
            if row[0]=='image1.fits' or row[0]=='image2.fits' or row[0]=='image3.fits' or row[0]=='image4.fits' or row[0]=='image5.fits':
                #print "se detecto imagen de prueba, voy a saltarmela"
                ni+=1
            else:
                #generar nueva lista sin comentarios
                comentario=row[12]
                del row[12]
                data.append(row)
                #poner comentarios en renglon aparte
                if len(comentario)>0:
                    #print "si hay comenatrios"
                    nc+=1
                    lista=[row[0],'Comentarios:',comentario]
                    lista_comentarios.append(lista)
                    #data.append(lista)
        else:
            #header por separado
            header.append(row)          
        conta+=1
    print "Encontre %d archivos de imagenes y los brinque"%ni
    print "Encontre %d Comentarios de las  imagenes "%nc
    return data, header
################################################################################################
def gen_file2(data,header, filename):
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter),
                        rightMargin=35,leftMargin=72,
                        topMargin=18,bottomMargin=18)
    
    # container for the 'Flowable' objects
    elements = []
    
    #sheet head
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    txt="Auto Log File by  Oan\'s CCD\'s"
    ptext = '<font size=14>%s</font>' % txt
     
    elements.append(Paragraph(ptext, styles["Normal"]))
    elements.append(Spacer(1, 12))

    
    # header info renglon 1 y 2
    ptext = " ".join(header[0])
    elements.append(Paragraph(ptext, styles["Normal"]))
    ptext = " ".join(header[1])
    elements.append(Paragraph(ptext, styles["Normal"]))
    ptext="Log file: "+filename
    elements.append(Paragraph(ptext, styles["Normal"]))
    #espacio
    elements.append(Spacer(1, 12))
    
    
    h=header[2]
    del h[12]
    # tabla datos --------------------------
    data.insert(0,h)
    t=Table(data)
    t.setStyle(TableStyle([
                            #('BACKGROUND',(1,0),(-1,-1),colors.yellow),
                            ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                            #('BACKGROUND',(0,0),(-1,0),colors.dimgray),
                            #('TEXTCOLOR',(0,0),(-1,0),colors.black)
                            ('LINEABOVE', (0,0), (-1,0), 2, colors.green),
                            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
                            ('COLBACKGROUNDS', (0, 0), (-1, -1), (None,0xC6E2FF,0xc8c8c8,0xc8c8c8,None,0xC6E2FF,0xc8c8c8,None,0xC6E2FF,0xc8c8c8,None,0xC6E2FF,0xc8c8c8 )) 
                            ]))
               
    elements.append(t)
    
    # tabla comentarios ----------------------
    if nc>=1:
        elements.append(Spacer(1, 0.5*inch)) #espacio
        
        ptext = '<font size=14>  Lista de Comentarios: </font>'
        elements.append(Paragraph(ptext, styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch)) #espacio
        
        C=Table(lista_comentarios)
        C.setStyle(TableStyle([
                                #('BACKGROUND',(1,0),(-1,-1),colors.yellow),
                                ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                                #('BACKGROUND',(0,0),(-1,0),colors.dimgray),
                                #('TEXTCOLOR',(0,0),(-1,0),colors.black)
                                ('LINEABOVE', (0,0), (-1,0), 2, colors.green),
                                ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                                ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
                                ('COLBACKGROUNDS', (0, 0), (-1, -1), (None,0xc8c8c8, 0xaaaaa0 )) 
                                ]))
                   
        elements.append(C)
        
    #nota final ------------------------------
    elements.append(Spacer(1, 48))
    ptext = '<font size=10>  UNAM-IA-OAN By colorado@astro.unam.mx ,  Python Powered!</font>'
    elements.append(Paragraph(ptext, styles["Normal"]))

    
    # write the document to disk
    doc.build(elements)

    return
########################################################################################
if __name__ == "__main__":
    arg = string.join(sys.argv[1:])
    print 'argumentos:',arg
    if len(arg) <4:
        print "Debes dar en el argumento el archivo .csv a procesar!!!!!!!!"
        print "los bitacoras estan en /imagenes/bitacora/"
        exit()
    
    
    data,header = process_csvfile2(arg)
    salida=arg[0:-3]+"pdf"
    print "archivo de salida=",salida
    gen_file2(data,header, salida)