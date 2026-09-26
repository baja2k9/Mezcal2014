#!/bin/bash
# Construye la cadena de imagenes en orden: py2gtk -> py2glade -> py2iraf
# Uso: ./build_all.sh [push]   (con "push" las sube a Docker Hub al terminar)
set -e

REPO=baja2k9
TAG=18.04
DIR="$(cd "$(dirname "$0")" && pwd)"

for img in py2gtk py2glade py2iraf; do
    echo "=== Construyendo $REPO/$img:$TAG"
    docker build \
        --build-arg USER_UID=$(id -u) \
        --build-arg USER_GID=$(id -g) \
        -t $REPO/$img:$TAG \
        "$DIR/$img"
done

if [ "$1" == "push" ]; then
    for img in py2gtk py2glade py2iraf; do
        docker push $REPO/$img:$TAG
    done
fi
