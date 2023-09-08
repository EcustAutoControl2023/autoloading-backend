
from flask import request


def process():
    if request.method == 'POST':
        return 'post'
    else:
        return 'get'