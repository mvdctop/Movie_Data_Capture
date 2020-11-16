#!/bin/sh

git fetch --all
git reset --hard origin/master
git pull

apt update
apt upgrade -y
pip3 install --upgrade -r requirements.txt
make
mv bin/* /avdc_bin

cd /avdc_bin
version=$(./AV_Data_Capture --version)
zip AV_Data_Capture-CLI-$(echo $version)-Linux-$(dpkg --print-architecture).zip AV_Data_Capture config.ini
