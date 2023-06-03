import ephem
from  c_util import *

import time, datetime
import math
try:
    import pytz
except:
    print '********** Error al importar pytz *********'


#DEPENDE DE -> pip install pyephem

#V 0.2 Colorado ->inicio
#V 0.3 Colorado ->uso de pyephem
#V 0.4 Colorado -> calculo de sunset y rising para el odrden de los filtros y polarizadores de los flats
#V 0.5 Colorado -> calculo de sunset y rising con twilight
#V 0.6 Colorado -> calculo de todos los twilight via 2 metodos, igual resultados, usar metodo 1
#V 0.7 Colorado -> calculo de utmiddle
#V 0.8 Colorado -> arregle bug, no actualizaba self.sky_state en compute_sun
#V0.9 Colorado ->anexe distancia angular entre objetos, pos. tel vs moon
#################################################################################################
class ASTRO(UTIL):
    'clase para calculo de datos astronomicos'

    Civil_twilight='-6'
    Nautical_twilight='-12'
    Astronomical_twilight='-18'
    Navy_twilight='-0:34'   #realmente no lo uso, pero deberia

    spm=ephem.Observer()

    def __init__(self):
        #print "CLASS ASTRO Ready...."
        #self.tijuana= pytz.timezone('America/Tijuana')
        self.jd=0
        self.ts=0
        self.epoca=2000
        self.airmass=1
        #self.spm=ephem.Observer()
        self.spm.lat='+31:02:40'
        self.spm.lon='-115:27:49'
        self.spm.elevation=2800
        self.spm.pressure = 0
        self.spm.horizon = 0
        self.sky_state='Nose'
        #self.sky_state_list=["Daylight","Civil Rising","Nautical Rising","Astronomical Rising","Daylight","Civil Setting","Nautical Setting","Night",]
        self.sky_state_list=["Daylight","Civil Dawn Twilight","Nautical Dawn Twilight","Astronomical Dawn Twilight",\
                             "Civil Dusk Twilight","Nautical Dusk Twilight","Astronomical Dusk","Night",]

        #self.test()
        self.utmiddle="0:0:0"
        self.ut="0:0:0"

#################################################################################################
    def dia_juliano (self):
        self.spm.date=ephem.now()
        self.ts=str( self.spm.sidereal_time() )
        self.jd=ephem.julian_date(ephem.now())
#################################################################################################
    def old_dia_juliano (self):
        #No lo uso
        rx="algo \n nada"
        try:
            rx=self.ejecuta("./astro")
        except:
            return

        #quitar espacios en blanco iniciales
        rx=rx.lstrip()
        t=rx.split(' ')
        #print "t=",t, " len=",len(t)
        t2=t[1].split('\n')
        self.jd=float(t2[0])
        t3=t[2].split('\n')
        self.ts=t3[0]

#################################################################################################
    def info (self):
        print "ut=",self.ut
        print "jd=",self.jd
        print "ts=",self.ts
        print "epoca=",self.epoca
        print "air mass=",self.airmass

#################################################################################################
    def epoca_actual (self):
        t=time.gmtime()
        #t=time.localtime(time.time())
        anio=int( t[0] )
        dias=int ( t[7] )
        epoca=anio+ (dias-1)/365.0
        self.epoca="%3.1f"%(epoca)

#################################################################################################
    def masa_aire (self,ah,dec):
        #print "calculando airmass %f %f"%(ah,dec)
        phi=0.5415611224834
        gra_rad=3.14159/180.0
        cosz=math.sin(phi)*math.sin(dec*gra_rad)+math.cos(phi)*math.cos(dec*gra_rad)*math.cos(ah*gra_rad)
        self.airmass=1/cosz
        return self.airmass
#################################################################################################
    # regresa 0, false si es PM, o sea si hay luz pero ya va a nochecer
    def esnoche_bad (self):
        #Ya no lo uso
        t=time.localtime(time.time())
        print t
        pm=time.strftime("%p", t)
        print "pm=",pm
        if pm=="PM":
            print "es noche, o sea va anochecer"
            return False
        else:
            print "es dia, va amanecer"
            return True
    #################################################################################################
    # false si es PM, o sea si hay luz pero ya va a nochecer, o sea el sunset
    def esnoche (self):
        self.compute_sunset()
        if self.delta_setting > self.delta_rise:
            #sunrise
            print "Va amanecer"
            return True
        else:
            #sunset
            print "Va a anochecer"
            return False


#################################################################################################
    def test(self):
        print 'prueba ephem'
        self.dia_juliano()
        self.epoca_actual()
        self.info()

        self.spm.date=ephem.now()
        st=self.spm.sidereal_time()
        jd=ephem.julian_date(ephem.now())

        print 'st',st
        print 'jd',jd
        N=self.esnoche()
        print N


#################################################################################################
    def compute_sunset(self):
        #sunrise
        delta=[]
        mydiff=[]
        self.spm.date=ephem.now()
        self.sun=sun=ephem.Sun()
        sun.compute(self.spm)

        #todos los amaneceres
        self.spm.horizon=0
        self.previous_rising=self.spm.previous_rising(sun, use_center=True)
        self.rising_time=self.spm.next_rising(sun, use_center=True)

        self.setting_time=self.spm.next_setting(sun, use_center=True)
        self.previous_setting=self.spm.previous_setting(sun, use_center=True)

        self.spm.horizon=self.Civil_twilight
        sun.compute(self.spm)
        self.Civil_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Civil_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Civil_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Civil_twilight_setting=self.spm.previous_setting(sun, use_center=True)


        self.spm.horizon=self.Nautical_twilight
        sun.compute(self.spm)
        self.Nautical_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Nautical_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Nautical_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Nautical_twilight_setting=self.spm.previous_setting(sun, use_center=True)


        self.spm.horizon=self.Astronomical_twilight
        sun.compute(self.spm)
        self.Astronomical_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Astronomical_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Astronomical_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Astronomical_twilight_setting=self.spm.previous_setting(sun, use_center=True)

        self.sky_info()


        #print setting_time.datetime()
        #metodo 1
        delta.append(self.spm.date-self.rising_time)
        delta.append(self.spm.date-self.Civil_twilight_rising)
        delta.append(self.spm.date-self.Nautical_twilight_rising)
        delta.append(self.spm.date-self.Astronomical_twilight_rising)

        delta.append(self.spm.date-self.setting_time)
        delta.append(self.spm.date-self.Civil_twilight_setting)
        delta.append(self.spm.date-self.Nautical_twilight_setting)
        delta.append(self.spm.date-self.Astronomical_twilight_setting)

        #diferencia en formato de fechas
        a=self.ephem_date_2_datetime(self.spm.date)
        b=self.ephem_date_2_datetime(self.rising_time)
        mydiff.append(b-a)
        mydiff.append(self.ephem_date_2_datetime(self.Civil_twilight_rising)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Nautical_twilight_rising)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Astronomical_twilight_rising)-a)

        mydiff.append(self.ephem_date_2_datetime(self.setting_time)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Civil_twilight_setting)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Nautical_twilight_setting)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Astronomical_twilight_setting)-a)


        self.mydiff=mydiff
        #Calcular el evento mas cercano
        min=2
        pos=0
        conta=0
        for d in delta:
            #print 'deltas',d
            if d< min:
                pos=conta
                min=d
            conta+=1
        print "min",min,pos,self.sky_state_list[pos]
        self.sky_state=self.sky_state_list[pos]
        #Fin metodo 1


        #para la rutina
        self.delta_rise=abs(self.rising_time-self.spm.date)
        print 'delta rising',self.delta_rise


        self.delta_setting=abs(self.setting_time-self.spm.date)
        print 'delta setting',self.delta_setting

        #sky state
        print 'sky state',self.sky_state
        self.sun=sun


#################################################################################################
    def compute_sky(self,date):
        #igual que compute_sunset, pero aqui le podemos dar otras fechas
        #sunrise
        delta=[]
        mydiff=[]
        debug=False

        self.spm.date=date
        sun=ephem.Sun()
        #print 'compute sky Date',date

        self.spm.horizon=0
        sun.compute(self.spm)
        self.previous_rising=self.spm.previous_rising(sun, use_center=True)
        self.rising_time=self.spm.next_rising(sun, use_center=True)

        self.setting_time=self.spm.next_setting(sun, use_center=True)
        self.previous_setting=self.spm.previous_setting(sun, use_center=True)

        #civil
        self.spm.horizon=self.Civil_twilight
        sun.compute(self.spm)
        self.Civil_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Civil_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Civil_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Civil_twilight_setting=self.spm.previous_setting(sun, use_center=True)

        #nautical
        self.spm.horizon=self.Nautical_twilight
        sun.compute(self.spm)
        self.Nautical_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Nautical_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Nautical_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Nautical_twilight_setting=self.spm.previous_setting(sun, use_center=True)

        #astro
        self.spm.horizon=self.Astronomical_twilight
        sun.compute(self.spm)
        self.Astronomical_twilight_rising=self.spm.next_rising(sun, use_center=True)
        self.previous_Astronomical_twilight_rising=self.spm.previous_rising(sun, use_center=True)

        self.Astronomical_twilight_setting=self.spm.next_setting(sun, use_center=True)
        self.previous_Astronomical_twilight_setting=self.spm.previous_setting(sun, use_center=True)

        if debug:
            self.sky_info()

        #print setting_time.datetime()
        delta.append(self.spm.date-self.rising_time)
        delta.append(self.spm.date-self.Civil_twilight_rising)
        delta.append(self.spm.date-self.Nautical_twilight_rising)
        delta.append(self.spm.date-self.Astronomical_twilight_rising)

        delta.append(self.spm.date-self.setting_time)
        delta.append(self.spm.date-self.Civil_twilight_setting)
        delta.append(self.spm.date-self.Nautical_twilight_setting)
        delta.append(self.spm.date-self.Astronomical_twilight_setting)

        #diferencia en formato de fechas
        a=self.ephem_date_2_datetime(self.spm.date)
        b=self.ephem_date_2_datetime(self.rising_time)
        mydiff.append(b-a)
        mydiff.append(self.ephem_date_2_datetime(self.Civil_twilight_rising)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Nautical_twilight_rising)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Astronomical_twilight_rising)-a)

        mydiff.append(self.ephem_date_2_datetime(self.setting_time)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Civil_twilight_setting)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Nautical_twilight_setting)-a)
        mydiff.append(self.ephem_date_2_datetime(self.Astronomical_twilight_setting)-a)

        max=2
        pos=0
        conta=0
        for d in delta:
            #print 'deltas',d
            if d <max:
                pos=conta
                max=d
            conta+=1
        #print "min",max,pos

        #sky state
        #print 'sky state',self.sky_state
        self.sun=sun
        return pos
#################################################################################################
    def sky_info(self):
        print "==================++++++++++++++++++++==================================="
        print "Rinse time:               ",self.rising_time,'Local:',ephem.localtime( self.rising_time)
        print "Civil Rising time:        ",self.Civil_twilight_rising,'Local:',ephem.localtime( self.Civil_twilight_rising)
        print "Nautilcal Rising time:    ",self.Nautical_twilight_rising,'Local:',ephem.localtime( self.Nautical_twilight_rising)
        print "Astronomical Rising time: ",self.Astronomical_twilight_rising,'Local:',ephem.localtime( self.Astronomical_twilight_rising)

        print "==================++++++++++++++++++++==================================="
        print "Setting time:             ",self.setting_time,'Local:',ephem.localtime(self.setting_time)
        print "Civil Setting time:       ",self.Civil_twilight_setting,'Local:',ephem.localtime(self.Civil_twilight_setting)
        print "Nautilcal Setting time:   ",self.Nautical_twilight_setting,'Local:',ephem.localtime(self.Nautical_twilight_setting)
        print "Astronomical Setting time:",self.Astronomical_twilight_setting,'Local:',ephem.localtime(self.Astronomical_twilight_setting)
        print "Now:                      ",self.spm.date,'Local:',ephem.localtime(self.spm.date)
        print "==================++++++++++++++++++++==================================="

#################################################################################################
    def sky_diff(self):
        print "==================++++++++++++++++++++==================================="
        print "Rinse time:               ",self.rising_time,'Diff:',self.mydiff[0]
        print "Civil Rising time:        ",self.Civil_twilight_rising,'Diff:',self.mydiff[1]
        print "Nautilcal Rising time:    ",self.Nautical_twilight_rising,'Diff:',self.mydiff[2]
        print "Astronomical Rising time: ",self.Astronomical_twilight_rising,'Diff:',self.mydiff[3]

        print "==================++++++++++++++++++++==================================="
        print "Setting time:             ",self.setting_time,'Diff:',self.mydiff[4]
        print "Civil Setting time:       ",self.Civil_twilight_setting,'Diff:',self.mydiff[5]
        print "Nautilcal Setting time:   ",self.Nautical_twilight_setting,'Diff:',self.mydiff[6]
        print "Astronomical Setting time:",self.Astronomical_twilight_setting,'Diff:',self.mydiff[7]
        print "Now:                      ",self.spm.date,'Local:',ephem.localtime(self.spm.date)
        print "==================++++++++++++++++++++==================================="
#################################################################################################
    def test2(self):
        #Probar como funcionana los 2 metodos
        print 'test2'
        #UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
        sun=ephem.Sun()

        start_date = datetime.datetime(2013, 3, 24,0,0,0)
        end_date = datetime.datetime(2013, 3, 24,23,59,59)
        td = datetime.timedelta(minutes=15)

        date = start_date
        pos=8
        while date < end_date:
            #udate=date
            pos=self.compute_sky(date)
            #udate=result_utc_datetime = date - UTC_OFFSET_TIMEDELTA

            #otro metodo
            d = ephem.Date(date)
            self.twilight(d)
            #print 'Sky State----->',A.sky_state

            #print date,pos,self.sky_state_list[pos],self.sky_state
            print date,pos,self.sky_state_list[pos],self.sun.alt,self.sun.az
            date += td
#################################################################################################
    def test3(self):
        #Probar como lo del sol
        print 'test3'

        sun=ephem.Sun()

        start_date = datetime.datetime(2013, 3, 24,0,0,0)
        end_date = datetime.datetime(2013, 3, 24,23,59,59)
        td = datetime.timedelta(minutes=15)

        date = start_date

        while date < end_date:
            #udate=date
            #pos=self.compute_sky(date)
            self.spm.date=date
            sun.compute(self.spm)

            d=self.date_to_angle(ephem.Date(date))
            print date,sun.alt,sun.az,d
            date += td
#################################################################################################
    def twilight(self, date=None):
        #print 'Calculando Twilight-------------------------------'
        #metodo 2, voy a usar mejor el otro

        if date==None:
            date=ephem.now()
        '''else:
            self.spm.date=date
        '''

        self.compute_sky(date)

        '''
        print 'Fecha',date,float(date)
        print 'pre ris',self.previous_rising,float(self.previous_rising),float(date-self.previous_rising)
        print 'set',self.setting_time,float(self.setting_time),float(date-self.setting_time)
        '''

        #print 'dia'
        #verificar si es de dia

        if date > self.previous_rising and date < self.setting_time:
            #Se ejecuta cuando las demas condiciones no se dan
            self.sky_state='Daylight'

        ok=self.check_zone(date,'rising','setting')
        if ok:
            self.sky_state='Daylight'

        #print 'civil'
        #if date >self.previous_setting and date<self.Civil_twilight_setting:

        ok=self.check_zone(date,'setting','civil_setting')
        if ok:
            self.sky_state='Civil Dusk Twilight'

        #print 'nautical'
        #if date >self.previous_Civil_twilight_setting and date<self.Nautical_twilight_setting:
        #    self.sky_state='Nautical Dusk Twilight'
        ok=self.check_zone(date,'civil_setting','nautical_setting')
        if ok:
            self.sky_state='Nautical Dusk Twilight'

        #print 'astro'
        #if date >self.previous_Nautical_twilight_setting and date<self.Astronomical_twilight_setting:
        #    self.sky_state='Astronimical Dusk Twilight'

        ok=self.check_zone(date,'nautical_setting','astronomical_setting')
        if ok:
            self.sky_state='Astronomical Dusk Twilight'

        #print 'noche'
        #c=get_closest_date(date,)
        #if date >self.previous_Astronomical_twilight_setting and date <self.Astronomical_twilight_rising:
        #    print "----------------Es de Noche"
        #    self.sky_state='Night'
        ok=self.check_zone(date,'astronomical_setting','astronomical_rising')
        if ok:
            self.sky_state='Night'


        #print 'dawn astro'
        '''
        if date >self.Astronomical_twilight_rising and date <self.Nautical_twilight_rising:
            self.sky_state='Astronimical Dawn Twilight'
            print 'dawn astro ok'
            return
        '''
        ok=self.check_zone(date,'astronomical_rising','nautical_rising')
        if ok:
            self.sky_state='Astronomical Dawn Twilight'


        #print 'dawn nautico'
        '''
        if date >self.Nautical_twilight_rising and date <self.Civil_twilight_rising:
            self.sky_state='Nautical Dawn Twilight'
            return
        '''
        ok=self.check_zone(date,'nautical_rising','civil_rising')
        if ok:
            self.sky_state='Nautical Dawn Twilight'

        #print 'dawn civil'
        '''
        print self.Civil_twilight_rising,float(self.Civil_twilight_rising)
        print self.rising_time,float(self.rising_time)

        if date >self.Civil_twilight_rising and date <self.rising_time:
            self.sky_state='Civil Dawn Twilight'
            return
        '''
        ok=self.check_zone(date,'civil_rising','rising')
        if ok:
            self.sky_state='Civil Dawn Twilight'


        #print self.sky_state
#################################################################################################
    def check_zone(self,date,ini='rising',fin='setting'):
        #checa en que zona esta la fecha, para metodo 2
        #print "check zone"
        ok=False

        if ini=='rising':
            beg=self.get_closest_date(date,self.previous_rising,self.rising_time)

        elif ini=='setting':
            beg=self.get_closest_date(date,self.previous_setting,self.setting_time)

        elif ini=='civil_setting':
            beg=self.get_closest_date(date,self.previous_Civil_twilight_setting,self.Civil_twilight_setting)

        elif ini=='civil_rising':
            beg=self.get_closest_date(date,self.previous_Civil_twilight_rising,self.Civil_twilight_rising)

        elif ini=='nautical_setting':
            beg=self.get_closest_date(date,self.previous_Nautical_twilight_setting,self.Nautical_twilight_setting)

        elif ini=='nautical_rising':
            beg=self.get_closest_date(date,self.previous_Nautical_twilight_rising,self.Nautical_twilight_rising)

        elif ini=='astronomical_setting':
            beg=self.get_closest_date(date,self.previous_Astronomical_twilight_setting,self.Astronomical_twilight_setting)

        elif ini=='astronomical_rising':
            beg=self.get_closest_date(date,self.previous_Astronomical_twilight_rising,self.Astronomical_twilight_rising)
        else:
            print "Error, No encontre ini:",ini

        #####
        if fin=='rising':
            end=self.get_closest_date(date,self.previous_rising,self.rising_time)

        elif fin=='setting':
            end=self.get_closest_date(date,self.previous_setting,self.setting_time)

        elif fin=='civil_setting':
            end=self.get_closest_date(date,self.previous_Civil_twilight_setting,self.Civil_twilight_setting)

        elif fin=='civil_rising':
            end=self.get_closest_date(date,self.previous_Civil_twilight_rising,self.Civil_twilight_rising)

        elif fin=='nautical_setting':
            end=self.get_closest_date(date,self.previous_Nautical_twilight_setting,self.Nautical_twilight_setting)

        elif fin=='nautical_rising':
            end=self.get_closest_date(date,self.previous_Nautical_twilight_rising,self.Nautical_twilight_rising)

        elif fin=='astronomical_setting':
            end=self.get_closest_date(date,self.previous_Astronomical_twilight_setting,self.Astronomical_twilight_setting)

        elif fin=='astronomical_rising':
            end=self.get_closest_date(date,self.previous_Astronomical_twilight_rising,self.Astronomical_twilight_rising)
        else:
            print "Error, No encontre fin:",fin


        if date > beg and date < end:
            ok=True


        #print "check zone ENDED....",ok
        return ok
#################################################################################################
    def get_closest_date(self,date,a,b):
        #regresa la fecha mas cercana

            if abs(date-a) < abs(date-b):
                #print "esta mas cerca el previus"
                beg=a
            else:
                #print "esta mas cerca el next "
                beg=b

            return beg
#################################################################################################
    def ephem_date_2_datetime(self, myephemdate):
        #self.kk=myephemdate

        sec=int(myephemdate.tuple()[5])
        mytime=datetime.datetime(myephemdate.tuple()[0],myephemdate.tuple()[1],myephemdate.tuple()[2],myephemdate.tuple()[3],myephemdate.tuple()[4],sec)
        return mytime

#################################################################################################
    def date_to_angle(self, myephemdate):
        #tiene que ser date tipo ephem
        sec=int(myephemdate.tuple()[5])
        mytime="%s:%s:%s"%(myephemdate.tuple()[3],myephemdate.tuple()[4],sec)
        #print myephemdate
        #print mytime
        t=ephem.hours(mytime)
        d=ephem.degrees(t)*180/ephem.pi
        #print d
        return d

#################################################################################################
    def compute_moon(self ):
        #next_moon=self.spm.next_
        self.spm.date=ephem.now()
        moon=ephem.Moon()
        moon.compute(self.spm)

        full_moon=ephem.next_full_moon(self.spm.date)
        moon_phase=moon.moon_phase*100.0
        new_moon=ephem.next_new_moon(self.spm.date)
        pre_new_moon=ephem.previous_new_moon(self.spm.date)

        #moon_transit=moon.transit_time
        #moon_rise=moon.rise_time
        #moon_set=moon.set_time
        moon_transit=self.spm.next_transit(moon)
        moon_rise=self.spm.next_rising(moon)
        moon_set=self.spm.next_setting(moon)



        #la fase no es lo mismo que la iluminacion
        lunation=(self.spm.date-pre_new_moon)/(new_moon-pre_new_moon)
        symbol=lunation*26
        if symbol < 0.2 or symbol > 25.8 :
            symbol = '1'  # new moon
        else:
            symbol = chr(ord('A')+int(symbol+0.5)-1)

        #print 'symbol',symbol,lunation



        self.moon=moon
        self.moon_phase=moon_phase
        self.full_moon=full_moon
        self.new_moon=new_moon

        self.moon_rise=moon_rise
        self.moon_transit=moon_transit
        self.moon_set=moon_set



#################################################################################################
    def moon_info(self ):
        print 'Moon Phase    ',self.moon_phase
        print 'Next Full Moon',self.full_moon,'Local:',ephem.localtime(self.full_moon)
        print 'Next New Moon ',self.new_moon,'Local:',ephem.localtime(self.new_moon)

        print 'Moonrise      ',self.moon_rise,'Local:',ephem.localtime(self.moon_rise)
        print 'Moon Transit  ',self.moon_transit,'Local:',ephem.localtime(self.moon_transit)
        print 'Moonset       ',self.moon_set,'Local:',ephem.localtime(self.moon_set)


#################################################################################################
    def calcula_ut_y_utmiddle(self,exp_sec):
        #exp_sec = tiempo de exposicion en segundos
        #tambien actualiza udate
        '''
        utmiddle = "utmiddle"
        The name of the output keyword that will receive the universal time for the middle of the observation.
        The format of the keyword will be the same as that specifying the universal time.
        '''

        utc=datetime.datetime.utcnow()
        self.ut="%2.2d:%2.2d:%2.2d.%3.3d"%(utc.hour,utc.minute,utc.second,utc.microsecond)
        self.udate="%d-%2.2d-%2.2d"%(utc.year,utc.month,utc.day)

        if exp_sec==0:
            mid=0
        else:
            mid=exp_sec/2.0

        td=datetime.timedelta(seconds=mid)
        #print "delta=",td

        #print "utc",utc
        utmiddle=utc+td
        #print "utmiddle",utmiddle
        self.utmiddle="%2.2d:%2.2d:%2.2d.%3.3d"%(utmiddle.hour,utmiddle.minute,utmiddle.second,utmiddle.microsecond)
        return self.utmiddle
###########################################################
    def HH_MM_SS_to_degrees(self,ra,separator=':'):
        (H,M,S)=ra.split(separator)
        try:
            DEG=(int(H)+float(M)/60.0+float(S)/3600.0)*15.0
        except:
            print "Error en conversion de RA a grados"
            DEG=-1

        return DEG
###########################################################
    def DD_MM_SS_to_decimal(self,dec,separator=':'):
        (D,M,S)=dec.split(separator)
        try:
            DEC=int(D)+float(M)/60.0+float(S)/3600.0
        except:
            print "Error en conversion de DEC a decimal"
            DEC=-1


        return DEC
#################################################################################################
    def dist_to_moon(self,ra,dec):
        print 'tel ra',ra
        print 'tel dec',dec
        #calcula la distancia angular entre tel y la luna
        #ra y dec en decimal

        #Moon
        self.spm.date = ephem.now()
        moon = ephem.Moon()
        moon.compute(self.spm)
        mar='moon AR='+str(moon.ra)
        mdec='moon DEC='+str(moon.dec)
        print mar
        print mdec


        az= "Azimuth="+str(moon.az)
        alt="Altitude="+str(moon.alt)
        print az
        print alt


        #A decimal
        mar=ephem.degrees(moon.ra)*180/ephem.pi
        mdec=ephem.degrees(moon.dec)*180/ephem.pi

        print mar
        print mdec

        #pasa todo a radianes
        mar=math.radians(mar)
        mdec=math.radians(mdec)
        #tel
        ra=math.radians(ra)
        dec=math.radians(dec)

        #formula de ilse
        self.d2_moon=math.degrees(math.acos(math.sin(mdec)*math.sin(dec)+math.cos(mdec)*math.cos(dec)*math.cos(mar-ra)))

        #grados
        print 'distancia hacia luna',self.d2_moon
        print 'moon phase',moon.moon_phase
        return self.d2_moon

#################################################################################################

#A=ASTRO()
#u=A.calcula_utmiddle(2,5)
#A.compute_sunset()
#A.twilight()
#print A.dist_to_moon(101.43,-16.514)
