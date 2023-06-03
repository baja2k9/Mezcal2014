#!/usr/bin/env python
# -*- coding: utf-8 -*-

import c_analisis

from c_analisis import *

class ANALISIS2(ANALISIS):


    def busca_imagenes(self,work_dir):
        #busca todas las imagenes en un directorio y las clasifica
        # como bias o imagenes en sus listas

        print "---------------------------------------"
        bias_list=[]    #lista de Bias
        image_list = [] #Lista de imagenes

        im_list = listdir(work_dir)
        #im_list = sort(array(im_list)) #sort

        #print work_dir
        #print im_list

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


        print "Lista de Bias ",self.bias_list
        print '*************/n/n/n'
        #print self.images_list

        #hacer set de imagenes de 3
        n=len(self.images_list)/3
        print 'Vamos a hacer %d sets de 3'%n

        print self.set_images_list
        self.set_images_list=self.images_list.reshape(n,3)
        #self.set_images_list.shape=(30,3)
        #print self.set_images_list


        #Sacar lista de tiempos
        for imagenes in self.set_images_list:
            print 'Procesando set de imagenes',imagenes
            #print imagenes[0]
            key=self.B.datos_keyword(imagenes[0],'PARAM58')
            self.lista_tiempo.append((key.value/1000))
