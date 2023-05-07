# If you can't run this script, please execute the following command in PowerShell.
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

$CLOUDSCRAPER_PATH = $( python -c 'import cloudscraper as _; print(_.__path__[0])' | select -Last 1 )
$OPENCC_PATH = $( python -c 'import opencc as _; print(_.__path__[0])' | select -Last 1 )
$FACE_RECOGNITION_MODELS = $( python -c 'import face_recognition_models as _; print(_.__path__[0])' | select -Last 1 )

mkdir build
mkdir __pycache__

pyinstaller --onefile Movie_Data_Capture.py `
    --hidden-import "ImageProcessing.cnn" `
    --python-option u `
    --add-data "$FACE_RECOGNITION_MODELS;face_recognition_models" `
    --add-data "$CLOUDSCRAPER_PATH;cloudscraper" `
    --add-data "$OPENCC_PATH;opencc" `
    --add-data "Img;Img" `
    --add-data "config.ini;." `
    --add-data "scrapinglib;scrapinglib" `

rmdir -Recurse -Force build
rmdir -Recurse -Force __pycache__
rmdir -Recurse -Force Movie_Data_Capture.spec

echo "[Make]Finish"
pause