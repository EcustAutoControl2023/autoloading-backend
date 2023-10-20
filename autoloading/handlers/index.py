from flask import redirect, render_template, request, session
from ..config import ENV
from autoloading.models.sensor import Traffic


def index():
    sp = session.get('show_popup', None)
    iu = session.get('img_url', None)
    if sp and iu is not None:
        return render_template('index.html', show_popup=sp, img_url=iu)
    traffics = Traffic.query.all()

    return render_template('index.html',traffics=traffics)

def login():
    # 跳过登录界面
    if ENV != 'production':
        return redirect('index')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username =='admin' and password == 'password':
            session['logged_in'] = True
            return redirect('index')
        else:
            return '无效密码或用户名'
    else:
        return render_template('dl.html')
