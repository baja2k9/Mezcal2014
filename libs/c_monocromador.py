import math
from math import pi, sin,cos

from c_cliente import *

###########################################################
class MONOCROMADOR(CLIENTE):
    'Manejo del monocromador oriel'

###########################################################
    def __init__(self,variables):
        self.mis_variables = variables
        self.debug=True
        self.ip="192.168.0.152"
        #self.ip="localhost"
        self.puerto=3333
        self.set_timeout(30)
        self.posicion=0
        self.deseada=0
        self.DELTETA= 2.59995
        self.K= 0.413858
        self.d= 0.000000833
        self.P=0
        self.F=0


###########################################################
    def inicializa(self):
        data,status=self.manda("INICIALIZA;")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi mono",data
        self.procesa_respuesta(data)
        return True

###########################################################
    def pide_posicion(self):
        if self.debug: print 'Mono pidiendo posicion...'
        data,status=self.manda("POSICION;")
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi mono",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def mueve_motor(self,posicion):
        '''
        4000 a
        4070.19820164
        Voy a mandar: MUEVE_MOTOR(995);
        '''

        print "moviendo mono a posicion ",posicion
        t="MUEVE_MOTOR(%d);"% posicion
        #t=tuple(t)
        data,status=self.manda(t)
        if not status:
            print "bad"
            print data
            return -1
        if self.debug: print "recibi",data
        self.procesa_respuesta(data)
        return True
###########################################################
    def procesa_respuesta(self,data):

        print "Rx=",data
        mando=data.split()
        key=mando[0]
        key2=mando[1]
        if key=="MEXMAN" and key2=="POS":
            if self.debug: print "llegaron filtros mexman.."
            self.f1=mando[2]
            self.f1_name=mando[3]
            self.f1=mando[4]
            self.f2_name=mando[5]
            self.filtro="%s + %s" %(self.f1_name,self.f2_name)
            if self.debug: print "el filtro es=",self.filtro
            #tupla = ["MEXMAN_UPDATE",self.filtro]
            txt="MEXMAN_UPDATE "+self.filtro
            self.mis_variables.queue.put(txt)
############################################################################
    def RL(self,P):
        self.P = P*pi/(200.0*180.0)
        self.F = self.d*1e10*(sin(self.K+self.P+self.DELTETA) + sin(self.P+self.DELTETA))
        return self.F
############################################################################
    def M(self,LAMBDA, P):
        '''
        print LAMBDA,P
        print self.d
        print self.K
        print self.DELTETA
        '''

        F=self.d*(sin(self.K+P+self.DELTETA)+sin(P+self.DELTETA))-LAMBDA
        FP=self.d*(cos(self.K+P+self.DELTETA)+cos(P+self.DELTETA))
        m=P-(F/FP)
        return m

############################################################################
    def VP(self,LAMBDA):
        P=0.0
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)
        P=self.M(LAMBDA,P)

        P=P*200.0*180.0/pi
        return P
############################################################################
    def mueve_lambda(self,pos):
        lam=pos/1e10
        valor2=int(round(self.VP(lam)))
        print 'Valor Pasos',valor2
        self.mueve_motor(valor2)



############################################################################


