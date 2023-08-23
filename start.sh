#!/bin/bash

# 等待数据库完全启动
sleep 7

# 如何环境变量TESTING为true，则启动测试服务器
if [ "$TESTING" = "true" ]; then
    echo "Testing server"
    flask run -p 8080 -h 0.0.0.0 --debug
else
    echo "Production server"
    gunicorn autoloading:app -c gunicorn.conf.py
fi