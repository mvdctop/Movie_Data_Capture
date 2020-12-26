pkg install python37 py37-requests py37-pip py37-lxml py37-pillow py37-cloudscraper py37-pysocks git zip py37-pyinstaller py37-beautifulsoup448
pip install pyquery
pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py
cp config.ini ./dist
