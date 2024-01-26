from flask import redirect, render_template, request, session
from ..config import ENV
from autoloading.models.sensor import Traffic


def index():
    sp = session.get('show_popup', None)
    iu = session.get('img_url', None)
    if sp and iu is not None:
        return render_template('index.html', show_popup=sp, img_url=iu)
    traffics1 = Traffic.query.all()

    return render_template('index.html',traffics=traffics1)


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

def index1():
    return render_template('index1.html')

def index2():
    return render_template('index2.html')

def index3():
    return render_template('index3.html')

def index4():
    return render_template('index4.html')

def index5():
    return render_template('index5.html')

def index6():
    return render_template('index6.html')

def index7():
    return render_template('index7.html')

def index8():
    return render_template('index8.html')

def index9():
    return render_template('index9.html')

def index10():
    return render_template('index10.html')

def index11():
    return render_template('index11.html')

def index12():
    return render_template('index12.html')

def index13():
    return render_template('index13.html')

def index14():
    return render_template('index14.html')

def index15():
    return render_template('index15.html')

def index16():
    return render_template('index16.html')

def index17():
    return render_template('index17.html')

def index18():
    return render_template('index18.html')

def index19():
    return render_template('index19.html')
