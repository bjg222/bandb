
from flask import redirect, session, render_template, request
from flask.helpers import url_for

from . import rsvp
from .sheets import RsvpSheet
from .forms import VerifyForm, ResponseForm, DetailsForm

@rsvp.route('/')
def main():
    if ('rsvp_id' not in session):
        return redirect(url_for('.verify'))
    if (not RsvpSheet().has_rsvp(session['rsvp_id'])):
        return redirect(url_for('.response'))
    return redirect(url_for('.summary'))

@rsvp.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerifyForm()
    if (form.validate_on_submit()):
        print(form.data)
        data = RsvpSheet().get_invitee(last_name=form.last_name.data, invite_code=form.invite_code.data)
        if (data is not None):
            print(data)
            session['rsvp_id'] = data['id']
            session['people'] = (data['people'] if isinstance(data['people'], list) else [data['people']])
            session['addressee'] = data['addressee']
            session['guest'] = data['guest']
            print(session)
            return redirect(url_for('.main'))
    else:
        print(form.errors)
    return render_template('verify.html', form=form)

@rsvp.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('.main'))

@rsvp.route('/reset')
def reset():
    data = RsvpSheet().get_invitee(rsvp_id=session['rsvp_id'])
    session.clear()
    if (data is not None):
        print(data)
        session['rsvp_id'] = data['id']
        session['people'] = (data['people'] if isinstance(data['people'], list) else [data['people']])
        session['addressee'] = data['addressee']
        session['guest'] = data['guest']
        print(session)
    return redirect(url_for('.main'))

@rsvp.route('/response', methods=['GET', 'POST'])
def response():
    if ('rsvp_id' not in session):
        return redirect(url_for('.main'))
    form = ResponseForm()
    if (form.validate_on_submit()):
        print(form.data)
        session['attending'] = bool(form.attending.data)
        if (not session['attending']):
            return redirect(url_for('.review'))
        return redirect(url_for('.details'))
    else:
        print(form.errors)
    return render_template('response.html', form=form)

@rsvp.route('/details', methods=['GET', 'POST'])
def details():
    if (not 'rsvp_id' in session):
        return redirect(url_for('.main'))
    form = DetailsForm()
    form.attendees.choices = [(idx, name) for idx, name in enumerate(session['people'])]
    if (session['guest']):
        form.attendees.choices.append((99, 'Guest'))
        form.guest.default = 'Guest of ' + session['addressee']
        if (not form.guest.data):
            form.guest.data = form.guest.default
    else:
        del form.guest
    if (form.validate_on_submit()):
        print(form.data)
        session['attendees'] = [session['people'][idx] for idx in form.attendees.data if idx < 99]
        if (session['guest'] and 99 in form.attendees.data):
            session['attendees'].append(form.guest.data)
        if (form.songs.data):
            session['songs'] = form.songs.data
        return redirect(url_for('.review'))
    else:
        print(form.errors)
    return render_template('details.html', form=form)

@rsvp.route('/review', methods=['GET', 'POST'])
def review():
    if (request.method == 'POST'):
        return redirect(url_for('.summary'))
    if ('rsvp_id' not in session or 'attending' not in session):
        return redirect(url_for('.main'))
    data = {'adressee': session['addressee'], 'response': session['attending']}
    if (session['attending']):
        data.update({'attendees': session['attendees']})
        if (session['songs']):
            data.update({'songs': session['songs']})
    return render_template('review.html', data=data)

@rsvp.route('/summary')
def summary():
    return 'summary'
