#! /bin/bash

echo "Mezcal Restart Iraf scrip ............"

#limpiar todo
./unload.py ./ds9 -title Mezcal >>/dev/null
./unload.py ./bin/ds9 -title Mezcal >>/dev/null

./unload.py /bin/csh -f /tmp/start_iraf_observa.devmezcal0

./unload.py /usr/local/mezcal/ds9 -title Mezcal

./unload.py /usr/local/mezcal/ds9 -title Mezcal -fifo ./.devmezcal0/imt1 -g +571+0

./unload.py /bin/csh -f /tmp/start_iraf_observa.devmezcal0


