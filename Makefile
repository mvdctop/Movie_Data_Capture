#.PHONY: help prepare-dev test lint run doc

#VENV_NAME?=venv
#VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
#PYTHON=${VENV_NAME}/bin/python3
SHELL = /bin/bash

.DEFAULT: make
make:
	@echo "[+]make prepare-dev"
	#sudo apt-get -y install python3 python3-pip
	pip3 install -r requirements.txt
	pip3 install pyinstaller

	#@echo "[+]Set CLOUDSCRAPER_PATH variable"
	#export cloudscraper_path=$(python3 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1)

	@echo "[+]Pyinstaller make"
	pyinstaller --onefile Movie_Data_Capture.py  --hidden-import ADC_function.py --hidden-import core.py \
	    --hidden-import "ImageProcessing.cnn" \
	    --python-option u \
		--add-data "`python3 -c 'import cloudscraper as _; print(_.__path__[0])' | tail -n 1`:cloudscraper" \
		--add-data "`python3 -c 'import opencc as _; print(_.__path__[0])' | tail -n 1`:opencc" \
        --add-data "`python3 -c 'import face_recognition_models as _; print(_.__path__[0])' | tail -n 1`:face_recognition_models" \
		--add-data "Img:Img" \
		--add-data "config.ini:." \

	@echo "[+]Move to bin"
	if [ ! -d "./bin" ];then  mkdir bin; fi
	mv dist/* bin/
	cp config.ini bin/
	rm -rf dist/

	@echo "[+]Clean cache"
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -type d | xargs rm -fr
	@find . -name '.pytest_cache' -type d | xargs rm -fr
	rm -rf build/
