#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_analisis

A=c_analisis.ANALISIS()

#overscan
#A.set_roi(2080,2100,100,120)
A.set_roi(1100,1200,850,950)

#A.id='>Marconi3 Left'
workdir='/imagenes/marconi3/left'

A.pdf_dir=workdir
A.busca_imagenes(workdir)

A.id='>Marconi3 left'
#A.busca_imagenes('/imagenes/marconi3/right')

#A.conta_bits_img('/imagenes/marconi3/right/right_0043o.fits')

A.calculo_bias(A.bias_list)
A.calculo_media(A.set_images_list)
#A.calculo_linealidad_dir()
A.calculo_linealidad_2()

A.calculo_varianza_resta(A.set_images_list)
A.calculo_final()

A.show()
