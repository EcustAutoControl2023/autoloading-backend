FROM python:3-slim

ENV FLASK_APP="autoloading"

WORKDIR /usr/src/app

COPY . .

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update --no-cache
RUN apt-get install -y --no-cache pkgconf mariadb-dev build-base libffi-dev openssl-dev
RUN apt-get install -y --no-cache \
    ffmpeg-dev \
    gfortran \
    libjpeg-turbo-dev \
    openblas-dev \
    openjpeg-dev \
    tiff-dev \
    zlib-dev
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 最终部署使用命令
# RUN pip install .
# CMD [ "gunicorn", "autoloading:app", "-c", "gunicorn.conf.py" ]

# 开发测试命令 
RUN pip install -e .
CMD ["flask", "run", "-p", "5000", "-h", "0.0.0.0", "--debug"]