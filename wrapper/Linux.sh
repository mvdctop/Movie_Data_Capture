#if [ '$(dpkg --print-architecture)' != 'amd64' ] || [ '$(dpkg --print-architecture)' != 'i386' ]; then
#	apt install python3 python3-pip git sudo libxml2-dev libxslt-dev build-essential wget nano libcmocka-dev libcmocka0 -y
#	apt install zlib* libjpeg-dev  -y
	#wget https://files.pythonhosted.org/packages/82/96/21ba3619647bac2b34b4996b2dbbea8e74a703767ce24192899d9153c058/pyinstaller-4.0.tar.gz
	#tar -zxvf pyinstaller-4.0.tar.gz
	#cd pyinstaller-4.0/bootloader
	#sed -i "s/                                        '-Werror',//" wscript
	#python3 ./waf distclean all
	#cd ../
	#python3 setup.py install
	#cd ../
#fi
pip3 install -r requirements.txt
pip3 install cloudscraper==1.2.52
pyinstaller --onefile Movie_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py \
    --hidden-import "ImageProcessing.cnn" \
    --python-option u \
    --add-data "$(python3 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1):cloudscraper" \
    --add-data "$(python3 -c 'import opencc as _; print(_.__path__[0])' | tail -n 1):opencc" \
    --add-data "$(python3 -c 'import face_recognition_models as _; print(_.__path__[0])' | tail -n 1):face_recognition_models" \
    --add-data "Img:Img" \
    --add-data "config.ini:." \

cp config.ini ./dist
