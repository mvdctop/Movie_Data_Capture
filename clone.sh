export http_proxy='http://192.168.2.2:1080'
export https_proxy='http://192.168.2.2:1080'
git fetch --all
git reset --hard origin/master
git pull
export http_proxy=''
export https_proxy=''
