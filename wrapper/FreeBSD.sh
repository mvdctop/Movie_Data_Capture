pkg install python38 py38-requests py38-pip py38-lxml py38-pillow py38-cloudscraper git zip py38-beautifulsoup448 py38-mechanicalsoup
pip install pyinstaller
pyinstaller --onefile Movie_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py \
    --hidden-import "ImageProcessing.cnn" \
    --add-data "$(python3.8 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1):cloudscraper" \
    --add-data "$(python3.8 -c 'import opencc as _; print(_.__path__[0])' | tail -n 1):opencc" \
    --add-data "$(python3.8 -c 'import face_recognition_models as _; print(_.__path__[0])' | tail -n 1):face_recognition_models" \
    --add-data "Img:Img" \
    --add-data "config.ini:." \

cp config.ini ./dist
