# Mezcal

Sistema de control del instrumento **Mezcal** para el telescopio de 2 metros del OAN (Observatorio Astronómico Nacional, San Pedro Mártir). Interfaz gráfica en Python/GTK2 que maneja ruedas de filtros, rejilla, obturador, lámparas, espejo, difusor y rotador (platina).

- Repositorio: https://github.com/baja2k9/Mezcal2014
- Versión actual: 2.23 (Jun 2023)
- Autor: E. Colorado

---

## Requisitos

- Ubuntu 20.04 LTS
- Python 2.7
- PyGTK 2.0
- DS9 + XPA (binarios en `bin/`)
- IRAF
- Librería del guiador: `/usr/local/instrumentacion/guiador2m_cliente`
- Librerías de CCDs: symlink `libs/ → ../oan_ccds/libs/`

---

## Instalación

```bash
# Crear symlink de librerías de CCDs
ln -s ../oan_ccds/libs/ .

# Verificar que bin/ tenga las ligas correctas para ds9 y xpa
ls bin/
```

El sistema se ejecuta desde `/usr/local/instrumentacion/Mezcal2014/`.

---

## Arranque

```bash
./runme          # Arranque completo: DS9 + IRAF + GUI de Mezcal
```

El script `runme`:
1. Termina instancias previas
2. Lanza DS9 en puerto 5139
3. Inicia terminal IRAF
4. Lee entorno desde `/tmp/marconi.kk`
5. Lanza `mezcal.py`

Otros scripts:
```bash
./init_ejes_mezcal.sh   # Inicializar ejes de motores
./restart_iraf.sh       # Reiniciar sesión IRAF
./umezcal               # Detener Mezcal
```

---

## Configuración

El archivo `/home/observa/mezcal.cfg` define las posiciones de ruedas, rendijas y filtros. Se lee al arrancar.

**Valores de foco de referencia:**
- Foco default: **2624 – 2626**
- Filtro CO+: **2500**

---

## Hardware controlado

Controlador de motores en `192.168.0.26:10001` — protocolo TCP/IP:

| Eje | Componente | Posiciones |
|-----|-----------|-----------|
| 1 | Rueda de filtros (Geneva) | 5 |
| 2 | Línea de filtros (Geneva) | 3 |
| 3 | Línea de filtros (Geneva) | 4 |
| 4 | Foco (potenciómetro) | continuo |
| 5 | Rejilla/grating (encoder) | continuo |
| 6 | Obturador | remoto/local |
| 7 | Lámparas, espejo y difusor | bits |

Platina (rotador) en `192.168.0.207:9999`.

**Lámparas:** Off / Tungsten / Th-Ar
**Rendijas:** 70 µm / 150 µm / Clear
**Filtros:** Hα 90Å, OIII 60Å, CO+, H₂O

---

## Protocolo de mandos (resumen)

Formato: `[A][Eje][OpCode][d3][d2][d1][d0];`

```
:A10;         Estado eje 1 (rueda 5pos)
:A13000N;     Mover rueda 5pos a posición N
:A43mnop;     Mover foco a posición mnop (hex mayúscula)
:A53mnop;     Mover rejilla a posición mnop (hex mayúscula)
:A620000;     Obturador ON, modo LOCAL
:A620011;     Obturador OFF, modo REMOTO
:A72mnpq;     Control lámparas/espejo/difusor
              m=0 lámpara1 ON, n=0 lámpara2 ON
              p=0 saca espejo, q=0 mete difusor
```

Ver `mandos_mezcal.txt` para referencia completa del protocolo.

---

## Secuencias (macros)

Las secuencias de observación están en `secuencias.mezcal`. Soportan `loop`/`endloop`. Secuencias disponibles:

| Nombre | Descripción |
|--------|-------------|
| `arc200-150` | Arco Th-Ar 200s, rendija 150 µm |
| `arc200-70` | Arco Th-Ar 200s, rendija 70 µm |
| `tungsten300_slit150` | Tungsten 300s, rendija 150 µm |
| `tungsten400_slit70` | Tungsten 400s, rendija 70 µm |
| `five_bias` | 5 bias con loop |
| `focus` | 20 exposiciones para foco |
| `slit_image_150` | Imagen de rendija 150 µm |
| `slit_image_70` | Imagen de rendija 70 µm |
| `expose` | Exposición simple |

---

## Logs de observación

Se generan automáticamente en `/imagenes/bitacora/`:
- `mez_bitacora_YYYY_MM_DD.log` — texto
- `mez_bitacora_YYYY_MM_DD.csv` — hoja de cálculo

Para convertir CSV a PDF: `mezcsv2pdf.py`
