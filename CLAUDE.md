# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mezcal** is a Python 2.7 GTK2-based GUI instrument control system for the 2-meter telescope at the OAN (Observatorio Astronómico Nacional). It controls a multi-channel spectroscopic instrument with filter wheels, gratings, shutters, lamps, and a rotator (platina), integrating with CCD cameras, DS9, and IRAF.

- Repo: https://github.com/baja2k9/Mezcal2014
- Production deployment: `/usr/local/instrumentacion/Mezcal2014/`
- Runtime OS: Ubuntu 20.04 LTS
- Python: **2.7** (uses old-style `print` statements, `thread` module, `Queue`)

## How to Run

```bash
./runme          # Full startup: unloads previous instance, launches DS9, IRAF, and mezcal GUI
./mezcal.py      # Launch GUI directly (requires environment already set up)
```

The `runme` script:
1. Unloads previous instances via `unload.py`
2. Launches DS9 on port 5139
3. Starts IRAF terminal
4. Sources `/tmp/marconi.kk` for CCD environment variables
5. Launches `mezcal.py`

Other useful scripts:
- `init_ejes_mezcal.sh` — Initialize hardware motor axes
- `restart_iraf.sh` — Restart IRAF session
- `umezcal` — Unload/stop mezcal

## Architecture

The application uses **multiple inheritance** as its primary composition pattern. The main `MEZCAL` class inherits from:
- `MEZCAL_MOTORES` (motor axis control)
- `BIN2FITS` (image format conversion, from `libs/c_bin2fits.py`)
- `BACKUP` (data backup, from `libs/c_backup_oan.py`)
- `GPLATINA` (rotator GUI handlers, from `c_gplatina.py`)

### Hardware Communication

All hardware uses TCP/IP sockets via the `CLIENTE` base class (`libs/c_cliente.py`):
- **Mezcal motors controller**: `192.168.0.26:10001` — 7 axes (filter wheels, focus, grating, shutter, lamps/mirror)
- **Platina (rotator)**: `192.168.0.207:9999` — position angle control

### Threading Model

- Main thread: GTK2 event loop (`gobject.threads_init()`)
- Worker threads: CCD exposure, motor movement
- Thread-safe IPC via `Queue.Queue` (state managed in `libs/c_variables.py`)

### Key Files

| File | Purpose |
|------|---------|
| `mezcal.py` | Main GUI (~3100 lines), GTK2 event handlers, exposure workflow |
| `mezcal_motores.py` | 7-axis motor control via TCP/IP |
| `c_platina2m.py` | Rotator (platina) position control, PA↔PL conversions |
| `c_gplatina.py` | GUI event handlers for platina |
| `c_mez_macros.py` | Macro sequence parser/executor for `secuencias.mezcal` |
| `c_config_mez.py` | Reads `/home/observa/mezcal.cfg` (wheel/slit/filter definitions) |
| `c_ambiente2.py` | Manages CCD environment variables |
| `libs/c_cliente.py` | TCP/IP socket base class |
| `libs/c_variables.py` | Shared state and message queue for GUI updates |
| `libs/c_analisis.py` | Image analysis, HFR focus measurement |
| `libs/c_ccd_*.py` | CCD camera implementations (15+ variants: MARCONI, SITE4, SITE5, FLI, SPECTRAL, etc.) |
| `libs/c_filtros_*.py` | Filter wheel position definitions (8 variants) |
| `mez.ui` | Glade XML UI definition |
| `secuencias.mezcal` | Macro sequence definitions (arc, bias, tungsten, focus sequences) |

### Configuration

- `/home/observa/mezcal.cfg` — wheel positions, slits, filters (read at runtime by `c_config_mez.py`)
- `mez.ui` — GTK Glade UI layout (referenced as `/usr/local/instrumentacion/Mezcal2014/mez.ui` in production)
- `mis_colores.rc` — GTK2 color theme
- `secuencias.mezcal` — observation macro sequences

### CCD Integration

CCD classes follow a hierarchy: specific camera class (e.g., `CCD_MARCONI`) → `CCD` base → inherits from `WEATHER`, `ASTRO`. The active CCD class is selected at startup based on environment/config. Image data flows through BIN2FITS conversion before DS9 display and FITS file writing.

### Observation Logging

Logs are written to `/imagenes/bitacora/` in two formats:
- `mez_bitacora_YYYY_MM_DD.log` — human-readable text
- `mez_bitacora_YYYY_MM_DD.csv` — spreadsheet with observation metadata

## Dependencies

No `requirements.txt`. Runtime dependencies:
- `pygtk 2.0`, `gtk`, `gobject` — GUI framework
- `/usr/local/instrumentacion/guiador2m_cliente` — guide camera library (symlinked)
- `libs/` — symlinked from `../oan_ccds/libs/` (see README note)
- DS9 + XPA — astronomy image viewer (binaries in `bin/`)
- IRAF — image reduction and analysis

## Focus Reference Values

- Default focus position: **2624–2626**
- CO+ filter focus: **2500**
