pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py
cp config.ini dist/
find . -name '*.pyc' -delete
find . -name '__pycache__' -type d | xargs rm -fr
find . -name '.pytest_cache' -type d | xargs rm -fr
rm -rf build/
