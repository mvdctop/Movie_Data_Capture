#!/bin/sh

git fetch --all
git reset --hard origin/master
git pull

apt update
apt upgrade -y
pip3 install --upgrade -r requirements.txt
make

cd bin
version=$(./AV_Data_Capture --version)
zip AV_Data_Capture-CLI-$(echo $version)-$(uname)-$(dpkg --print-architecture).zip AV_Data_Capture config.ini
mv *zip /avdc_bin
