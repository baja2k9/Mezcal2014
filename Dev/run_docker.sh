#!/bin/bash

# Habilitar acceso X11 local para Wayland/XWayland
xhost +local: 2>/dev/null

#docker pull fediazs91/fdiaz_oan_ccd:latest
docker run  -u observa \
            --net=host \
            --env "DISPLAY" \
            --env "XAUTHORITY=/tmp/.Xauthority" \
            --env "OAN_MQTT_PUERTO=1884" \
            --env "OAN_SPECTRAL_IP=localhost" \
            -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
            -v ${XAUTHORITY:-$HOME/.Xauthority}:/tmp/.Xauthority:ro \
           -v /home/colorado/Progs/Telescopios/Tel15/oan_ccds:/usr/local/instrumentacion/oan_ccds \
            -v $HOME/Progs/Telescopios/Tel2m/Mezcal2014:/usr/local/instrumentacion/Mezcal2014 \
            -v $HOME/Progs/Telescopios/Tel2m/guiador2m_cliente:/usr/local/instrumentacion/guiador2m_cliente \
            -v $HOME/Progs/Telescopios/Tel2m/Mezcal2014/mezcal.cfg:/home/observa/mezcal.cfg:ro \
           -v /imagenes:/imagenes \
           -v /imagenes:/home/observa/imagenes \
           -w /usr/local/instrumentacion/Mezcal2014 \
           --rm \
           -it \
           colorado/oan_py2:18.04 \
           /bin/bash


