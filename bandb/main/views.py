
from flask import redirect, session, render_template, request, flash

from . import main

def is_dev_mode():
    return request.args.get('dev') is not None

@main.route('/')
def index():
    return render_template('main/index.html', dev=is_dev_mode())

@main.route('/hotel')
def hotel():
    return render_template('main/hotel.html', dev=is_dev_mode())
