# If you can't run this script, please execute the following command in PowerShell.
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# bugfix：set submodules find path
$Env:PYTHONPATH=$pwd.path
$PYTHONPATH=$pwd.path
mkdir build
mkdir __pycache__

pyinstaller --collect-submodules "ImageProcessing" `
    --collect-data "face_recognition_models" `
    --collect-data "cloudscraper" `
    --collect-data "opencc" `
    --add-data "Img;Img" `
    --add-data "config.ini;." `
    --add-data "scrapinglib;scrapinglib" `
    --onefile Movie_Data_Capture.py


rmdir -Recurse -Force build
rmdir -Recurse -Force __pycache__
rmdir -Recurse -Force Movie_Data_Capture.spec

echo "[Make]Finish"
pause
