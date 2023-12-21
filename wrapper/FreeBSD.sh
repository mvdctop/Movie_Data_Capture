pkg install python39 py39-requests py39-pip py39-lxml py39-pillow py39-cloudscraper py39-pysocks git zip py39-beautifulsoup448 py39-mechanicalsoup
pip install pyinstaller
pyinstaller --onefile Movie_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py \
    --hidden-import "ImageProcessing.cnn" \
    --python-option u \
    --add-data "$(python3.9 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1):cloudscraper" \
    --add-data "$(python3.9 -c 'import opencc as _; print(_.__path__[0])' | tail -n 1):opencc" \
    --add-data "$(python3.9 -c 'import face_recognition_models as _; print(_.__path__[0])' | tail -n 1):face_recognition_models" \
    --add-data "Img:Img" \
    --add-data "config.ini:." \

cp config.ini ./dist
