# oan_py2

Entorno **Python 2.7 + GTK2 + IRAF + DS9** sobre **Ubuntu 18.04**, para correr en PCs modernas el software de instrumentación del Observatorio Astronómico Nacional (OAN-SPM): control de CCDs (`oan_ccds`), Mezcal y otros proyectos heredados que requieren Python 2.

## Contenido

| Componente | Versión / detalle |
|---|---|
| Sistema base | Ubuntu 18.04.6 LTS (x86_64) |
| Python | 2.7.17 + python3 |
| GUI | PyGTK 2.24, python-gobject, python-glade2, **Glade 3.8.2** (`glade-3`) |
| Científico | numpy, scipy, matplotlib, pyfits 3.4, reportlab |
| Astronomía | **IRAF 2.17.1** (`cl`), **x11iraf 2.1** (`xgterm`, `ximtool`), **PyRAF 2.1.14**, **SAOImage DS9** + XPA, pyds9, astrometry.net (`solve-field`), ephem, python3-imexam |
| Comunicaciones | paho-mqtt 1.6.1, mosquitto-clients, netpipes |
| Utilerías | git, cvs, tcsh, tcl, imagemagick, daemontools, nano, ping, build-essential, cfitsio |

- **Usuario:** `observa` (uid/gid 1000) con `sudo` sin contraseña. IRAF ya está inicializado (`~/.iraf`, `~/uparm`).
- **Zona horaria:** `America/Tijuana`.
- **Directorio de trabajo:** `/usr/local/instrumentacion/oan_ccds/`
- **Comando por defecto:** `./runme`
- **Tamaño:** ~5 GB descomprimida.

## Uso

Descarga:

```bash
docker pull baja2k9/oan_py2:18.04
```

Ejecución con soporte gráfico (X11 / XWayland) y red del host, necesaria para hablar con el hardware por TCP/IP y con DS9/XPA:

```bash
xhost +local:
docker run -u observa --net=host \
    --env DISPLAY --env XAUTHORITY=/tmp/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v ${XAUTHORITY:-$HOME/.Xauthority}:/tmp/.Xauthority:ro \
    -v /ruta/a/oan_ccds:/usr/local/instrumentacion/oan_ccds \
    -v /imagenes:/imagenes \
    --rm -it baja2k9/oan_py2:18.04
```

Por defecto ejecuta `./runme` de `oan_ccds`, así que hay que montar ese proyecto en `/usr/local/instrumentacion/oan_ccds`. Para entrar a una terminal, agrega `/bin/bash` al final del comando.

### Ejemplo: Mezcal (telescopio de 2 m)

```bash
docker run -u observa --net=host \
    --env DISPLAY --env XAUTHORITY=/tmp/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v ${XAUTHORITY:-$HOME/.Xauthority}:/tmp/.Xauthority:ro \
    -v /ruta/a/oan_ccds:/usr/local/instrumentacion/oan_ccds \
    -v /ruta/a/Mezcal2014:/usr/local/instrumentacion/Mezcal2014 \
    -v /ruta/a/guiador2m_cliente:/usr/local/instrumentacion/guiador2m_cliente \
    -v /ruta/a/mezcal.cfg:/home/observa/mezcal.cfg:ro \
    -v /imagenes:/imagenes \
    -w /usr/local/instrumentacion/Mezcal2014 \
    --rm -it baja2k9/oan_py2:18.04 ./runme
```

## Notas

- Monta los proyectos en las mismas rutas que usan en producción (`/usr/local/instrumentacion/...`), porque el código usa rutas absolutas.
- Si tu usuario del host no tiene uid 1000, los archivos que se escriban en volúmenes montados quedarán con otro dueño.
- Ubuntu 18.04 ya no tiene soporte estándar. Esta imagen existe para preservar software heredado, no para exponer servicios a internet.

## Fuente

Dockerfile: https://github.com/baja2k9/Mezcal2014 (directorio `Dev/`)

Mantenedor: E. Colorado — OAN, Instituto de Astronomía UNAM
