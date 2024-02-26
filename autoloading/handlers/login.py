from flask import redirect, render_template, request, session
from ..config import ENV

def login():
    # 跳过登录界面
    if ENV != 'production':
        return redirect('index1')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username =='admin' and password == 'password':
            session['logged_in'] = True
            return redirect('index1')
        else:
            return '无效密码或用户名'
    else:
        return render_template('login.html')
