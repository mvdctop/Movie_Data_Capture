#! /bin/bash

git fetch --all
git reset --hard origin/master
git pull

apt update
apt upgrade -y
pip3 install --upgrade -r requirements.txt
make
mv bin/* /avdc_bin/
