
from flask import redirect, session, render_template, request, flash
from flask.helpers import url_for

from . import rsvp
from .sheets import RsvpSheet
from .forms import VerifyForm, ResponseForm, DetailsForm, SubmitForm

def get_rsvp_sheet():
    s = RsvpSheet()
    if (s.has_error()):
        raise s.get_error()
    return s

@rsvp.route('/')
def main():
    if ('rsvp_id' not in session):
        flash('Welcome, please verify your invitation')
        return redirect(url_for('.verify'))
    sh = get_rsvp_sheet()
    if (not sh.has_rsvp(session['rsvp_id'])):
        flash('Welcome, please RSVP')
        return redirect(url_for('.response'))
    data = sh.get_rsvp(session['rsvp_id'])
    if (data['people']):
        session['attending'] = True
        session['attendees'] = data['people']
    else:
        session['attending'] = False
    flash('Welcome back, your RSVP is below')
    return redirect(url_for('.summary'))

@rsvp.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerifyForm()
    if (form.validate_on_submit()):
        print(form.data)
        data = get_rsvp_sheet().get_invitee(last_name=form.last_name.data, invite_code=form.invite_code.data)
        if (data is not None):
            print(data)
            session['rsvp_id'] = data['id']
            session['people'] = (data['people'] if isinstance(data['people'], list) else [data['people']])
            session['addressee'] = data['addressee']
            session['guest'] = data['guest']
            print(session)
            flash('Thanks for verifying your invitation')
            return redirect(url_for('.main'))
    elif (form.errors):
        flash(form.errors)
    return render_template('verify.html', form=form)

@rsvp.route('/clear')
def clear():
    session.clear()
    flash('Session cleared')
    return redirect(url_for('.main'))

@rsvp.route('/reset')
def reset():
    data = get_rsvp_sheet().get_invitee(rsvp_id=session['rsvp_id'])
    session.clear()
    if (data is not None):
        print(data)
        session['rsvp_id'] = data['id']
        session['people'] = (data['people'] if isinstance(data['people'], list) else [data['people']])
        session['addressee'] = data['addressee']
        session['guest'] = data['guest']
        print(session)
    flash('Session reset')
    return redirect(url_for('.main'))

@rsvp.route('/response', methods=['GET', 'POST'])
def response():
    if ('rsvp_id' not in session):
        flash('Please verify your invitation first')
        return redirect(url_for('.main'))
    form = ResponseForm()
    if (form.validate_on_submit()):
        print(form.data)
        session['attending'] = bool(form.attending.data)
        if (not session['attending']):
            flash('We\'re sorry you can\'t make it.  Please confirm your RSVP.')
            return redirect(url_for('.review'))
        flash('We\'re thrilled you can make it!  Please provide some more details.')
        return redirect(url_for('.details'))
    elif (form.errors):
        flash(form.errors)
    return render_template('response.html', form=form)

@rsvp.route('/details', methods=['GET', 'POST'])
def details():
    if (not 'rsvp_id' in session):
        flash('Please verify your invitation first')
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
            session['bringing_guest'] = True
            session['attendees'].append(form.guest.data)
        if (form.diet.data):
            session['diet'] = form.diet.data.strip()
        if (form.songs.data):
            session['songs'] = [song.strip() for song in form.songs.data if song.strip()]
        flash('Thanks for providing us some info!  Please confirm your RSVP')
        return redirect(url_for('.review'))
    elif (form.errors):
        flash(form.errors)
    return render_template('details.html', form=form)

@rsvp.route('/review', methods=['GET', 'POST'])
def review():
    if ('rsvp_id' not in session):
        flash('Please verify your invitation first')
        return redirect(url_for('.main'))
    if ('attending' not in session):
        flash('Please complete your RSVP first')
        return redirect(url_for('.main'))
    form = SubmitForm()
    if (form.validate_on_submit()):
        res = get_rsvp_sheet().save_rsvp(session['rsvp_id'], 
                                         session['addressee'], 
                                         session['attendees'] if session['attending'] else None, 
                                         True if 'bringing_guest' in session and session['bringing_guest'] else False, 
                                         session['songs'] if 'songs' in session else None, 
                                         session['diet'] if 'diet' in session else None)
        flash('RSVP Saved')
        return redirect(url_for('.summary'))
    elif (form.errors):
        flash(form.errors)
    data = {key: session[key] for key in ['addressee', 'attending', 'attendees', 'diet', 'songs'] if key in session}
    return render_template('review.html', data=data, form=form)

@rsvp.route('/summary')
def summary():
    if ('rsvp_id' not in session):
        flash('Please verify your invitation first')
        return redirect(url_for('.main'))
    if ('attending' not in session):
        flash('Please complete your RSVP first')
        return redirect(url_for('.main'))
    data = {key: session[key] for key in ['addressee', 'attending', 'attendees'] if key in session}
    return render_template('summary.html', data=data)
    