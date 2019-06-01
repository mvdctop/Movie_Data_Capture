pyinstaller --onefile AV_Data_Capture.py 
pyinstaller --onefile core.py --hidden-import ADC_function.py --hidden-import fc2fans_club.py --hidden-import javbus.py --hidden-import siro.py