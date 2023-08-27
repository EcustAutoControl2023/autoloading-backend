FROM python:3

ENV FLASK_APP="autoloading"

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 最终部署使用命令
# RUN pip install .
# CMD [ "gunicorn", "autoloading:app", "-c", "gunicorn.conf.py" ]

# 开发测试命令 
RUN pip install -e .
CMD ["flask", "run", "-p", "5000", "-h", "0.0.0.0", "--debug"]