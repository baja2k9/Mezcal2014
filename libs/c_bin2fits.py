#!/usr/bin/python
# -*- coding: utf-8 -*-
#import math
import pyfits

from c_ccd import *

# V2.00 Ago-2015, E. Colorado ->por cambio de os y librerias de pyfits este libreria la dividi en 2 old y new
# V2.1  Mar-2016  E.Colorado => hice mas eficiente el cambio de clase segun version de pyfits ya me funciono bien en
#                               kubuntu 10.04, 12 y 14, tambien en mac os el capitan
############################################################################
############################################################################
#verificar la version en uso
ver=pyfits.__dict__['__version__']
print "Version de pyfits:",ver
if ver=='1.3':
    #usado en ubuntu 10.04
    print "VOY A USAR BIN2FITS VIEJO"
    import c_bin2fits_old
    from c_bin2fits_old import *

else:
    #usado en ubuntu 14.04, mejor dicho pyfits >3.0
    print "VOY A USAR BIN2FITS NUEVO"
    import c_bin2fits_new
    from c_bin2fits_new import *


############################################################################
############################################################################


class BIN2FITS(BIN2FITS_MAIN):
    mi_ccd = c_ccd.CCD()
############################################################################
    def __init__(self):
            BIN2FITS_MAIN.__init__(self)

############################################################################
#f=BIN2FITS()
#f.myinfo()
