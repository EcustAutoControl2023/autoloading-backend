from flask import redirect, session, url_for

def popup():
    session['show_popup'] = True
    return redirect(url_for('index'))

def popup_confirm():
    session['show_popup'] = False
    session['img_url'] = None
    return redirect(url_for('index'))
