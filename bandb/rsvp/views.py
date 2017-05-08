
from flask import redirect, session, render_template, request
from flask.helpers import url_for

from . import rsvp
from .sheets import RsvpSheet
from .forms import VerifyForm, RsvpForm
from bandb.rsvp.forms import RsvpDetailsForm

@rsvp.route('/')
def main():
    if (not 'rsvp_id' in session):
        return redirect(url_for('.verify'))
    if (not RsvpSheet().has_rsvp(session['rsvp_id'])):
        return redirect(url_for('.form'))
    return redirect(url_for('.summary'))

@rsvp.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerifyForm()
    if (form.validate_on_submit()):
        data = RsvpSheet().get_invitee(last_name=form.last_name.data, invite_code=form.invite_code.data)
        if (data is not None):
            print(data)
            session['rsvp_id'] = data['id']
            session['people'] = (data['people'] if isinstance(data['people'], list) else [data['people']])
            session['addressee'] = data['addressee']
            session['guest'] = data['guest']
            print(session)
            return redirect(url_for('.main'))
    return render_template('verify.html', form=form)

@rsvp.route('/reverify')
def reverify():
    session.clear()
    return redirect(url_for('.main'))

@rsvp.route('/form', methods=['GET', 'POST'])
def form():
    rsvp = RsvpForm()
    details = RsvpDetailsForm()
    details.attendees.choices = [(idx, name) for idx, name in enumerate(session['people'])]
    if (session['guest']):
        details.attendees.choices.append((99, 'Guest'))
        details.guest.default = 'Guest of ' + session['addressee']
    else:
        del details.guest
    form = rsvp
    if (rsvp.validate_on_submit()):
        session['attending'] = bool(rsvp.attending.data)
        if (not session['attending']):
            return redirect(url_for('.review'))
        form = details
    elif (details.validate_on_submit()):
        session['attendees'] = [session['people'][idx] for idx in details.attendees.data if idx < 99]
        if (session['guest'] and 99 in details.attendees.data):
            session['attendees'].append(details.guest)
        return redirect(url_for('.review'))
    return render_template('form.html', form=form)

@rsvp.route('/review')
def review():
    print(session)
    return 'review'

@rsvp.route('/edit')
def edit():
    return 'edit'

@rsvp.route('/summary')
def summary():
    return 'summary'

@rsvp.route('/done')
def done():
    return 'done'