#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import sys

def kill_process(process_name):
    try:
        # Obtener la lista de procesos que coinciden con el nombre dado
        cmd = ["ps", "-ef"]
        output = subprocess.check_output(cmd)

        # Buscar el proceso en la lista
        for line in output.splitlines():
            if process_name in line:
                # Obtener el ID del proceso
                process_info = line.split()
                pid = process_info[1]

                # Matar el proceso
                subprocess.call(["kill", pid])
                print("Proceso {} terminado.".format(process_name))
                return

        # Si no se encontró el proceso
        print("No se encontró el proceso {}.".format(process_name))

    except subprocess.CalledProcessError as e:
        print("Error al obtener la lista de procesos: {}".format(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python2 kill_process.py <nombre_del_proceso>")
    else:
        process_name = sys.argv[1]
        kill_process(process_name)