FROM python:slim
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN apt-get update \
    && apt-get install -y wget ca-certificates \
    && wget -O - 'https://github.com/yoshiko2/AV_Data_Capture/archive/master.tar.gz' | tar xz \
    && mv AV_Data_Capture-master /jav \
    && cd /jav \
    && ( pip install --no-cache-dir -r requirements.txt || true ) \
    && pip install --no-cache-dir requests lxml Beautifulsoup4 pillow \
    && apt-get purge -y wget

WORKDIR /jav
