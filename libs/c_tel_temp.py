#!/usr/bin/env python
#para el tel 15m
class TEL_TEMP:
	archivo="/imagenes/temperatura15/temperatura15.txt"
	t_primario=0
	t_secundario=0
	t_aire=0
	
	
	def lee_temp(self):
		#print "leyendo temp "
		#print self.archivo
		try:	
			openfile = open(self.archivo, 'r')
		except:
			#print "Error, no pude abrir ",self.archivo
			return False 
		
		str=openfile.read()
		openfile.close()
		t=str.split()
		if len(t)<6:
			print "no hay suficientes datos"
			return False
		self.t_primario=t[1]
		self.t_secundario=t[3]
		self.t_aire=t[5]
		return True
		
	def info(self):
		print "temperatura telescopio"
		print "primario",self.t_primario
		print "secundario",self.t_secundario
		print "aire",self.t_aire

