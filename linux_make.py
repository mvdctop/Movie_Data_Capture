import os
os.system("pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py")
os.system("rm -rf ./build")
os.system("rm -rf ./__pycache__")
os.system("rm -rf AV_Data_Capture.spec")
os.system("echo '[Make]Finish'")
