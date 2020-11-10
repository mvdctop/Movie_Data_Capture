#! /bin/bash

git fetch --all
git reset --hard origin/master
git pull

apt update
apt upgrade -y
pip3 install --upgrade -r requirements.txt
make
mv bin/* /avdc_bin

cd /avdc_bin
zip AV_Data_Capture-CLI-$(./AV_Data_Capture --version)-linux-$(uname -m).zip AV_Data_Capture config.ini
