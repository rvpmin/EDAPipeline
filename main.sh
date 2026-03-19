#!/bin/bash

echo "Ejecutando pipeline EDA..."

python3 scripts/eda.py -i data/Base.xlsx

echo "Reporte generado en out/Reporte.pdf"