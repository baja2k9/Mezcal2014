# -*- coding: utf-8 -*-
import sys

sys.path.append("libs")
from c_cliente import *


# V0.1 E. Colorado, inicial Jun-2015 ->aqui va lo no grafico de platina
############################################################################
class PLATINA2M(CLIENTE):

    def __init__(self):
        print 'init platina2m'
        CLIENTE.__init__(self)

        self.ip="192.168.0.207"
        self.puerto=9999
        self.set_timeout(1)
        self.usuario='Platina2m'
        self.angulo = -1.0
        self.PA2=-1.0
        self.DEBUG=False

############################################################################
    def estado(self):
        #print 'estado platina 2m'
        data, status = self.manda('ESTADO')
        if not status:
            #print "bad"
            #print data
            return False
        
        #print data
        p=data.split('=')
        #print p[1]
        #print p
        a=p[1].split()
        #print 'a=',a
        try:
            self.angulo=float(a[0])
        except:
            print 'no pude sacar angulo de platina2m'
            self.angulo=-1
            
        #siempre positivo
        if self.angulo <0:
            self.angulo=360+self.angulo
            
        self.angulo=round(self.angulo,3)
        #print 'angulo Platina 2m=',self.angulo
        return True
############################################################################
    def PA_2_PL(self,PA):
        if PA < 0:
            PL = 0 - PA
        elif PA > 90 and PA <= 180:
            PL = 0 - (PA - 180)
        elif PA <= 90:
            PL = 360 - PA
        else:  # PA > 0
            PL = 360 - (PA - 180)

        return PL
############################################################################
    def PL_2_PA_old(self, PL):
        if PL < 0:
            PA = 0 - PL
        elif PL >= 0 and PL <=90:
            PA =  360-PL
        elif PL > 90 and PL <= 180:
            PA = 180 - PL
        else:  # PA > 0
            PA = 360 - (PL - 180)

        return PA

############################################################################
    def PL_2_PA(self, PL):
        PA2=''
        if PL < 0:
            PA = 0 - PL

        elif PL >= 0 and PL <= 90:
            PA = 360 - PL
            PA2=-PL
        elif PL > 90 and PL <= 180:
            PA = 360 - PL
            PA2 = -PL
        else:  # PA > 0
            PA = 360 - PL
            PA2 = -PL


        self.PA2=PA2
        return PA


############################################################################


P=PLATINA2M()
P.estado()

'''
for x in range(0,361,15):
    print 'PA=',x,'PL=',P.PA_2_PL(x)

print 'PA=',-15,'PL=',P.PA_2_PL(-15)

print 40*'*'

for x in range(0,361,15):
    print 'PL=',x,'PA=',P.PL_2_PA(x),'PA2=',P.PA2

print 'PL=',-15,'PA=',P.PL_2_PA(-15)

'''
