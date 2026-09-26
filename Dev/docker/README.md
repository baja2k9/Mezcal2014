# Imágenes Docker para proyectos Python 2 del OAN

Cadena de imágenes Docker, basadas en Ubuntu 18.04, para correr proyectos viejos en Python 2.7 + GTK2 (Mezcal, oan_ccds, etc.) en PCs que ya no tienen Python 2. Reemplazan a `fediazs91/fdiaz_oan_ccd`.

Cada imagen parte de la anterior. Así cada proyecto usa solo el nivel que necesita, y en disco las capas comunes se guardan una sola vez.

```
baja2k9/py2gtk:18.04      nivel 1  python2 + gtk2 + ds9/xpa
        │ FROM
baja2k9/py2glade:18.04    nivel 2  + glade3
        │ FROM
baja2k9/py2iraf:18.04     nivel 3  + IRAF + x11iraf + pyraf  (la más pesada)
```

## Contenido

| Imagen | Agrega | Uso típico |
|---|---|---|
| `py2gtk` | python2, pygtk2, python-glade2, numpy, scipy, matplotlib, pyfits, reportlab, saods9, xpa-tools, pyds9, cfitsio, ephem, pytz, paho-mqtt (1.x), mosquitto-clients, netpipes, daemontools, git, imagemagick, nano, etc. | GUIs GTK2 sin IRAF |
| `py2glade` | glade3 3.8.2 compilado desde fuente (diseñador de interfaces GTK2) | Editar archivos `.ui` / `.glade` |
| `py2iraf` | IRAF 2.17.1 (`/iraf/iraf`), x11iraf 2.1 (xgterm, ximtool), pyraf, astrometry.net, python3 + imexam, `mkiraf` ya inicializado para `observa` | Mezcal, oan_ccds, reducción de datos |

En todas las imágenes:
- El usuario es `observa` (uid/gid 1000 por defecto) y tiene `sudo` sin contraseña.
- La zona horaria es `America/Tijuana`.
- El contenedor arranca en `/bin/bash`, y cada proyecto decide qué ejecutar.

## Archivos

```
Dev/docker/
├── README.md
├── build_all.sh              construye las 3 imágenes en orden
├── py2gtk/Dockerfile
├── py2glade/Dockerfile
│   └── glade3-3.8.2.tar.xz   fuente de glade (lo usa ADD)
└── py2iraf/Dockerfile
```

## Construir

```bash
cd Dev/docker
./build_all.sh          # construye py2gtk -> py2glade -> py2iraf
./build_all.sh push     # construye y sube a Docker Hub
```

`build_all.sh` pasa tu uid/gid como `USER_UID`/`USER_GID`. Así los archivos que el contenedor escriba en volúmenes montados te pertenecen a ti.

Para construir una sola imagen (hay que respetar el orden, porque cada una necesita la anterior):

```bash
docker build -t baja2k9/py2gtk:18.04   py2gtk
docker build -t baja2k9/py2glade:18.04 py2glade
docker build -t baja2k9/py2iraf:18.04  py2iraf
```

### Cambiar la base

`py2glade` y `py2iraf` reciben su imagen base con `ARG BASE`. Por ejemplo, para tener IRAF **sin** glade:

```bash
docker build --build-arg BASE=baja2k9/py2gtk:18.04 -t baja2k9/py2iraf-noglade:18.04 py2iraf
```

Las versiones de IRAF y x11iraf también se pueden cambiar:

```bash
docker build --build-arg IRAF_VERSION=2.18 --build-arg X11IRAF_VERSION=2.1 -t baja2k9/py2iraf:18.04 py2iraf
```

## Subir y descargar (Docker Hub)

```bash
docker login -u baja2k9          # usa un Personal Access Token, no la contraseña
docker push baja2k9/py2iraf:18.04
docker pull baja2k9/py2iraf:18.04   # en otra PC
```

## Correr

Ejemplo mínimo con soporte gráfico (X11 / XWayland):

```bash
xhost +local: 2>/dev/null
docker run -u observa --net=host \
    --env DISPLAY --env XAUTHORITY=/tmp/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v ${XAUTHORITY:-$HOME/.Xauthority}:/tmp/.Xauthority:ro \
    -v $HOME/mi_proyecto:/usr/local/instrumentacion/mi_proyecto \
    -w /usr/local/instrumentacion/mi_proyecto \
    --rm -it baja2k9/py2iraf:18.04 /bin/bash
```

- `--net=host` hace falta para hablar con el hardware por TCP/IP y con DS9/XPA.
- Monta cada proyecto en la misma ruta que usa en producción (`/usr/local/instrumentacion/...`), para que funcionen las rutas absolutas del código.
- Para un ejemplo completo de Mezcal, ve `../run_docker.sh`.

Para verificar que todo esté bien dentro del contenedor:

```bash
python2 -c "import gtk, gobject, pyfits, numpy, ephem, paho.mqtt.client; print 'ok'"
which ds9 xpaset cl xgterm glade-3
```

## Notas y posibles problemas

- **Paquetes pip:** tienen versiones fijas porque las versiones recientes ya no soportan Python 2. No las actualices sin probar.
- **`python-pyraf` / `iraf-dev`:** vienen de apt y conviven con el IRAF compilado a mano, igual que en el Dockerfile original. Si llega a haber conflicto, aparecerá al construir `py2iraf`.
- **`mkiraf`:** se corre con `echo xgterm | mkiraf`. Si falla en el build, quita esa línea y corre `mkiraf` a mano dentro del contenedor.
- **Ubuntu 18.04:** ya no tiene soporte estándar. Si algún día `apt` deja de encontrar paquetes, hay que apuntar `sources.list` a `old-releases.ubuntu.com`.
- **Dockerfile viejo:** el Dockerfile monolítico original sigue en `../Dockerfile` como referencia.
