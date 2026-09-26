# Nivel 3 (el mas pesado): py2glade + IRAF 2.17.1 + x11iraf + pyraf + astrometry.net
ARG BASE=baja2k9/py2glade:18.04
FROM $BASE

ARG IRAF_VERSION=2.17.1
ARG X11IRAF_VERSION=2.1

USER root

# Dependencias de compilacion de IRAF y x11iraf, pyraf y herramientas python3
RUN apt-get update && apt-get install -y \
        gcc make flex bison zlib1g-dev \
        libcurl4-openssl-dev libexpat-dev libreadline-dev \
        libncurses-dev tcl-dev \
        libxaw7-dev libxmu-dev xaw3dg-dev libxpm-dev \
        python-pyraf iraf-dev astrometry.net \
        python3-pip cython python3-matplotlib python3-imexam python3-pyfits \
    && rm -rf /var/lib/apt/lists/*

# IRAF compilado desde fuente en /iraf/iraf
RUN mkdir -p /iraf && cd /iraf \
    && wget -q https://github.com/iraf-community/iraf/archive/refs/tags/v${IRAF_VERSION}.tar.gz \
    && tar zxf v${IRAF_VERSION}.tar.gz \
    && rm v${IRAF_VERSION}.tar.gz \
    && mv iraf-${IRAF_VERSION} iraf \
    && cd iraf \
    && make -j4 2>&1 | tee build.log \
    && make install \
    && chown -R observa:observa /iraf/iraf

# x11iraf (xgterm, ximtool)
RUN cd /iraf \
    && wget -q https://github.com/iraf-community/x11iraf/archive/refs/tags/v${X11IRAF_VERSION}.tar.gz \
    && tar xzf v${X11IRAF_VERSION}.tar.gz \
    && rm v${X11IRAF_VERSION}.tar.gz \
    && cd x11iraf-${X11IRAF_VERSION} \
    && make -j4 \
    && make install \
    && rm -rf /iraf/x11iraf-${X11IRAF_VERSION}

USER observa
WORKDIR /home/observa
# mkiraf pregunta el tipo de terminal; se le responde xgterm
RUN echo xgterm | mkiraf
CMD ["/bin/bash"]
