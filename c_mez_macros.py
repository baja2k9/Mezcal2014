#!/usr/bin/env python
# -*- coding: utf-8 -*-
#. E. Colorado-2014
############################################################################
class MEZMACROS():

############################################################################
    def __init__(self):
        print 'Class Mez macro loader'
        self.macro_file='secuencias.mezcal'
        self.lista_macros=[]
        self.lista_nombres=[]
        self.dict_lista={}


        self.load_macro()
        self.procesa_macros()
        self.expande_loop()
        #print self.lista_nombres

############################################################################
    def reload_macro(self,macro='secuencias.mezcal'):
        self.macro_file=macro
        self.lista_macros=[]
        self.lista_nombres=[]
        self.dict_lista={}

        self.load_macro()
        self.procesa_macros()
        self.expande_loop()
############################################################################
    def load_macro(self):
        print 'cargando macro=',self.macro_file
        try:
            openfile = open(self.macro_file, 'r')
        except:
            print "Error, no pude abrir ",self.macro_file
            return False

        str=openfile.read()
        openfile.close()
        self.lista_macros=str.split('\n')
        return True
############################################################################
    def procesa_macros(self):
        #print self.lista_macros
        bloque_name='inicio'

        for linea in self.lista_macros:
            #print "----- linea=",i

            #print linea[0:3]
            if linea[0:6]!='nombre' and linea[0:3]!='fin':
                #print "in ->",linea
                lista.append(linea)
            '''
            else:
                print "out",linea
            '''

            if linea[0:6]=='nombre':
                a=linea.split()
                #print '>>>>>nuevo bloque',a[1]
                bloque_name=a[1]
                self.lista_nombres.append(a[1])
                #hacer nueva lista
                lista=[]


            if linea[0:3]=='fin':
                #print "acabe bloque<<<<<"
                #salvar lista creada
                self.dict_lista[bloque_name]=lista

############################################################################
    def get_sub_macro(self,name):
        #regresa lista de submacros
        return self.dict_lista[name]
############################################################################
#busca los loop y pone los pasos repetidos sin loop
    def expande_loop(self):
        print 'expande loop'

        for nombre in self.lista_nombres:
            #print 'name',nombre
            lista=self.dict_lista[nombre]
            cambio,otra_lista=self.analiza_lista(lista)
            if cambio:
                print 'update lista', nombre
                self.dict_lista[nombre]=otra_lista

############################################################################
    def analiza_lista(self,lista):
        #print '****** analizando ***** '

        graba=False
        se_modifico=False
        lista_inicio=[]
        lista_final=[]
        lista_loop=[]
        lista_full=[]
        mini_lista=[]
        npaso=0

        inicio=True #controla grabar los pasos iniciales
        final=False #controla grabar los pasos finales

        for paso in lista:
            #print paso,len(paso)
            paso=paso.strip()
            if len(paso)>0:
                #print len(paso)

                if final:
                    lista_final.append(paso)
                if paso[0:7]=='endloop':
                    #print 'encontre enloop'
                    graba=False
                    final=True

                if graba:
                    mini_lista.append(paso)

                if paso[0:4]=='loop':
                    se_modifico=True
                    inicio=False
                    arg = paso.split()
                    npaso=int(arg[1])
                    #print 'encontre loop',npaso
                    mini_lista=[]
                    graba=True

                if inicio:
                    lista_inicio.append(paso)

        #print 'lista inicial',lista_inicio
        #print 'mini:',mini_lista
        #print 'lista final',lista_final

        #hacer lista expandida del puro loop

        for n in range(npaso):
            #print n
            for paso in mini_lista:
                lista_loop.append(paso)

        #print 'lista final',lista_loop
        #armar la lista final completa
        for paso in lista_inicio:
            lista_full.append(paso)

        for paso in lista_loop:
            lista_full.append(paso)

        for paso in lista_final:
            lista_full.append(paso)

        #print 'lista full final completa',lista_full
        #print '****** analizando End ***** '
        return se_modifico,lista_full
############################################################################

m=MEZMACROS()
