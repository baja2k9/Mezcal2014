#!/bin/dash
# Hazael: Este script es para forzar inicializar los ejes de wheel, slits y filters en el Mezcal.
#        Esto es necesario cuando se reinicia el Mezcal y los carros y la rueda no estan en su 
#        posicion de inicio, Este script es solo mientras se corrige el problema de que el Mezcal 
#        no renicia estos ejes en automatico al encender.

exec echo ":A12;" | nc -q0 192.168.0.26 10001
sleep 1
exec echo ":A22;" | nc -q0 192.168.0.26 10001
sleep 1
exec echo ":A32;" | nc -q0 192.168.0.26 10001
 
