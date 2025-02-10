wm title . "Mezcal-Rejilla"
wm geometry . 155x175
wm resizable . 0 0

set ip_addres "192.168.0.26"
set puerto "10001"


button .mueved1 -text ">"    -command {  exec echo ":A561;" | nc -q0 $ip_addres $puerto }
button .mueved2 -text ">>"   -command {  exec echo ":A562;" | nc -q0 $ip_addres $puerto }
button .mueved3 -text ">>>"  -command {  exec echo ":A563;" | nc -q0 $ip_addres $puerto }
button .muevei1 -text "<"    -command {  exec echo ":A571;" | nc -q0 $ip_addres $puerto }
button .muevei2 -text "<<"   -command {  exec echo ":A572;" | nc -q0 $ip_addres $puerto }
button .muevei3 -text "<<<"  -command {  exec echo ":A573;" | nc -q0 $ip_addres $puerto }
button .inicial -text "Init Grating"   -command {  exec echo ":A52;" | nc -q0 $ip_addres $puerto }
button .inicial2 -text "Init Slits"   -command {  exec echo ":A22;" | nc -q0 $ip_addres $puerto }
button .inicial3 -text "Init Filters"   -command {  exec echo ":A32;" | nc -q0 $ip_addres $puerto }

place .mueved1 -x 80 -y 15 -width 60 -height 20
place .mueved2 -x 80 -y 40 -width 60 -height 20
place .mueved3 -x 80 -y 65 -width 60 -height 20
place .muevei1 -x 15 -y 15 -width 60 -height 20
place .muevei2 -x 15 -y 40 -width 60 -height 20
place .muevei3 -x 15 -y 65 -width 60 -height 20
place .inicial -x 15 -y 90 -width 125 -height 20
place .inicial2 -x 15 -y 115 -width 125 -height 20
place .inicial3 -x 15 -y 140 -width 125 -height 20


after 1000 actualiza

proc actualiza {} {
   after 1000 actualiza
}

