#!/bin/bash

rm -rf build dist

python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name BaixadorNFe \
    baixar_notas.py
