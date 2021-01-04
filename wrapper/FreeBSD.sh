pkg install python37 py37-requests py37-pip py37-lxml py37-pillow py37-cloudscraper py37-pysocks git zip py37-pyinstaller py37-beautifulsoup448
pip install pyquery
pyinstaller --onefile AV_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py --add-data "$(python3.7 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1):cloudscraper"
cp config.ini ./dist
