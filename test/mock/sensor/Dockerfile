FROM python:3.10

# ENV FLASK_APP="autoloading"

# 修改时区
ENV TZ Asia/Shanghai

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 开发测试命令 
# RUN pip install -e .
# CMD ["flask", "run", "-p", "5000", "-h", "0.0.0.0", "--debug"]

CMD ["python", "main.py"]
