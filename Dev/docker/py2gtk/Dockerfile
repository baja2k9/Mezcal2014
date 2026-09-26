# Imagen base: python2 + gtk2 + herramientas astronomicas ligeras (ds9, xpa)
# Nivel 1 de la cadena: py2gtk -> py2glade -> py2iraf
FROM --platform=linux/x86_64 ubuntu:18.04

ENV TZ=America/Tijuana \
    DEBIAN_FRONTEND=noninteractive

ARG USERNAME=observa
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV USER=$USERNAME

# Usuario observa con sudo sin password
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# Python2 + gtk2 + librerias cientificas + ds9/xpa + utilerias
RUN apt-get update && apt-get install -y \
        python-dev python-pip \
        python-gtk2 python-gobject python-glade2 python-libxml2 \
        python-numpy python-scipy python-matplotlib python-pyfits python-reportlab \
        saods9 xpa-tools python-pyds9 libcfitsio-dev \
        build-essential libx11-dev wget git cvs \
        netpipes daemontools mosquitto-clients \
        tcsh tcl beep imagemagick iputils-ping nano \
    && rm -rf /var/lib/apt/lists/*

# Paquetes pip con versiones fijas que aun soportan python2
RUN pip install "ephem==3.7.7.1" "pytz==2021.3" "paho-mqtt==1.6.1"

USER $USERNAME
WORKDIR /home/$USERNAME
CMD ["/bin/bash"]
