pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py
rmdir /s/q build
rmdir /s/q __pycache__
pause