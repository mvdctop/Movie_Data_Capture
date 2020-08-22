#!/bin/bash

CLOUDSCRAPER_PATH=$(python -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1)

pyinstaller --onefile AV_Data_Capture.py \
    --hidden-import ADC_function.py \
    --hidden-import core.py \
    --add-data "$CLOUDSCRAPER_PATH:cloudscraper"

rm -rf build
rm -rf __pycache__
rm -rf AV_Data_Capture.spec

echo "[Make]Finish"
read -n 1
