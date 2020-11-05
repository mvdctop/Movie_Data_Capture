#! /bin/bash

git fetch --all
git reset --hard origin/master
git pull

apt update
apt upgrade -y
pip3 install --upgrade -r requirements.txt
make
mv bin/* /avdc_bin
version=$(python3 ./AV_Data_Capture.py --version)

cd /avdc_bin
zip AV_Data_Capture-CLI-$(version)-linux-$(uname -m).zip AV_Data_Capture config.ini
