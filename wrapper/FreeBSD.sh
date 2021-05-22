pkg install python38 py38-requests py38-pip py38-lxml py38-pillow py38-cloudscraper py38-pysocks git zip py38-beautifulsoup448
pip install pyquery pyinstaller
pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py --add-data "$(python3.8 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1):cloudscraper"
cp config.ini ./dist
