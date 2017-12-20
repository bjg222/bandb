
from flask import render_template, request, flash

from . import main
from .forms import EmailForm

def is_dev_mode():
    return request.args.get('dev') is not None

@main.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    errors = None
    if (form.validate_on_submit()):
        with open('emails.txt', 'a+') as f:
            f.write(form.name.data + ',' + form.email.data + '\n')
        form = None
    elif (form.errors):
        #flash(form.errors)
        errors = form.errors
    return render_template('main/index.html', dev=is_dev_mode(), form=form, errors=errors)

@main.route('/hotel')
def hotel():
    return render_template('main/hotel.html', dev=is_dev_mode())
