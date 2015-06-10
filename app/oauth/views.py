from flask import Blueprint, request, redirect, url_for, flash, session, g, abort, render_template
from app.extensions import db, login_user, oauth, current_user
from app.models import User
from providers import providers
import requests
import os

oauth_bp = Blueprint('oauth', __name__)

google = oauth.remote_app('google', **providers['google'])
facebook = oauth.remote_app('facebook', **providers['facebook'])
twitter = oauth.remote_app('twitter', **providers['twitter'])

remote_apps = oauth.remote_apps

GOOGLE_OAUTH2_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


@oauth_bp.route('/<provider>-login')
def oauth_login(provider):
    if provider not in remote_apps.keys():
        abort(404)

    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return render_template('close-popup.html')

    return remote_apps[provider].authorize(url_for('oauth.%s_authorized' % provider, _external=True))


# TODO: Fix oauth flash messages after login
@oauth_bp.route('/oauth2callback')
@google.authorized_handler
def google_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description'])

    session['google_oauth_token'] = (resp['access_token'], '')
    userinfo = requests.get(GOOGLE_OAUTH2_USERINFO_URL, params=dict(access_token=resp['access_token'])).json()

    print userinfo
    print session
    user = User.query.filter_by(username=userinfo['email']).first()
    if not user:
        user = User(username=userinfo['email'], email=userinfo['email'], pwdhash='')
        db.session.add(user)
        db.session.commit()
        session['change-username-allowed'] = True
    login_user(user)
    flash('Logged in as id=%s name=%s' % (userinfo['id'], userinfo['name']), 'success')
    # return redirect(url_for('frontend.index'))
    return render_template('close-popup.html')


@oauth_bp.route('/twitter-login/authorized')
@twitter.authorized_handler
def twitter_authorized(resp):
    print resp

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['twitter_oauth_token'] = resp['oauth_token'] + \
                                     resp['oauth_token_secret']
    user = User.query.filter_by(username=resp['screen_name']).first()
    if not user:
        user = User(username=resp['screen_name'], pwdhash='')
        db.session.add(user)
        db.session.commit()
        session['change-username-allowed'] = True
    login_user(user)
    flash('Logged in as twitter handle=%s' % resp['screen_name'], 'success')
    return render_template('close-popup.html')


@oauth_bp.route('/facebook-login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    user = User.query.filter_by(username=me.data['email']).first()
    if not user:
        user = User(username=me.data['email'], pwdhash='')
        db.session.add(user)
        db.session.commit()
        session['change-username-allowed'] = True

    login_user(user)
    flash('Logged in as id=%s name=%s' % (me.data['id'], me.data['name']), 'success')
    return render_template('close-popup.html')


@twitter.tokengetter
def get_twitter_oauth_token():
    return session.get('twitter_oauth_token')


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_oauth_token')


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')