from flask import redirect, session, url_for

def popup():
    session['show_popup'] = True
    # TODO:弹窗后的逻辑
    return redirect(url_for('index'))

def popup_confirm():
    session['show_popup'] = False
    session['img_url'] = None
    # TODO:确认之后的逻辑
    return redirect(url_for('index'))