# Nivel 2: py2gtk + glade3 (disenador de interfaces gtk2)
# Requiere glade3-3.8.2.tar.xz en este mismo directorio
ARG BASE=baja2k9/py2gtk:18.04
FROM $BASE

USER root

# Dependencias de compilacion de glade3
RUN apt-get update && apt-get install -y \
        libgtk2.0-dev libxml2-dev libglib2.0-dev intltool \
    && rm -rf /var/lib/apt/lists/*

# ADD descomprime el tar.xz automaticamente
ADD glade3-3.8.2.tar.xz /glade
RUN cd /glade/glade3-3.8.2 \
    && ./configure \
    && make -j4 \
    && make install \
    && ldconfig \
    && rm -rf /glade

USER observa
WORKDIR /home/observa
CMD ["/bin/bash"]
