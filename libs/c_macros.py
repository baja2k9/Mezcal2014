#cosas para los macros y el plugin

class MACROS():
    #del ltt
    TMON=1
    TINC=0.2
    NSTEP=4
    #para el autofoco del 84
    FOCO_STEP =21
    FOCO_DELTA = 15
    FOCO_INIT = 2626
    ccd=None
    funciones=None
    
    #para macro de los flats
    MIN_PIX=15000
    MAX_PIX=30000
    OPTIMAL_PIX=20000
    MIN_TIME=0.8
    MAX_TIME=100
    N_FLATS=5
    FILTER_LIST=1
    MOVE_DEC=0
    MOVE_AR=0
    
####################################################################    
    def __init__(self):
        pass
	#self.ccd = ccd
        #self.funciones=funciones
####################################################################
    def prueba(self,dato):
        print "mi prueba"
	self.funciones['test'](5)

####################################################################
####################################################################

