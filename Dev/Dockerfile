FROM --platform=linux/x86_64 ubuntu:18.04

ENV TZ=America/Tijuana \
    DEBIAN_FRONTEND=noninteractive
RUN apt-get update

ARG USERNAME=observa
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV USER=observa
# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME




# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************

# [Optional] Set the default user. Omit if you want to keep the default as root.

RUN apt-get -yu  --show-progress install python-numpy python-pyfits python-reportlab python-pip python-scipy python-matplotlib python-libxml2 python-dev netpipes build-essential libx11-dev saods9 cvs beep tcsh tcl
RUN apt-get -yu  --show-progress install python-pyds9 xpa-tools git libcfitsio-dev python-glade2 daemontools mosquitto-clients python-gobject python-gtk2 
RUN apt-get -yu  --show-progress install astrometry.net
RUN apt-get -yu install python-pyraf
RUN pip install pyephem
RUN pip install pytz
RUN pip install paho-mqtt
RUN apt install wget -y
RUN apt install gcc make flex bison zlib1g-dev -y
RUN apt install libcurl4-openssl-dev libexpat-dev libreadline-dev -y
RUN apt install imagemagick -y

RUN mkdir /iraf
WORKDIR /iraf
RUN wget https://github.com/iraf-community/iraf/archive/refs/tags/v2.17.1.tar.gz
RUN tar zxf v2.17.1.tar.gz
RUN mv iraf-2.17.1 iraf
WORKDIR /iraf/iraf 
RUN make -j4 2>&1 | tee build.log
RUN make install
WORKDIR /iraf
RUN chown -R observa:observa iraf
WORKDIR /iraf 
RUN apt install gcc make bison flex libncurses-dev tcl-dev -y 
RUN apt install libxaw7-dev libxmu-dev xaw3dg-dev libxpm-dev -y 
RUN apt install iraf-dev -y 
RUN wget https://github.com/iraf-community/x11iraf/archive/refs/tags/v2.1.tar.gz
RUN tar xzf v2.1.tar.gz
WORKDIR /iraf/x11iraf-2.1/
RUN make -j4 
RUN make install 

#instalar glade
RUN apt-get install build-essential libgtk2.0-dev libxml2-dev libglib2.0-dev intltool -y
RUN mkdir /glade
ADD glade3-3.8.2.tar.xz /glade
WORKDIR /glade/glade3-3.8.2
RUN /bin/bash -c './configure'
RUN make
RUN make install
RUN ldconfig

RUN apt-get install iputils-ping -y
RUN apt install nano -y
RUN apt install python3-pip -y
RUN apt install cython -y
RUN apt install python3-matplotlib -y
RUN apt install python3-imexam -y
RUN apt install python3-pyfits -y
WORKDIR /home/observa
USER $USERNAME
RUN mkiraf
WORKDIR /usr/local/instrumentacion/oan_ccds/  
CMD ["./runme"]
