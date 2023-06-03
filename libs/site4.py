#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_analisis

A=c_analisis.ANALISIS()

#overscan
#A.set_roi(2080,2100,100,120)
A.set_roi(510,540,405,435)
#A.id='>Marconi3 Left'
#A.busca_imagenes('/imagenes/marconi3/left')
A.id='>Site4'
workdir='/imagenes/kkk'
A.full_well=300000
A.pdf_dir=workdir


A.busca_imagenes(workdir)

#A.conta_bits_img('/imagenes/marconi3/right/right_0043o.fits')

A.calculo_bias(A.bias_list)
A.calculo_media(A.set_images_list)

A.calculo_linealidad_dir()
A.calculo_linealidad_2()



A.calculo_varianza_resta(A.set_images_list)
A.calculo_final()

#A.calculo_linealidad_3()
A.show_tabla()
A.show()
