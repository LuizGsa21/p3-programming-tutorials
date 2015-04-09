from flask import Blueprint, request, redirect, url_for, flash, session, g
from app.extensions import db, login_user, oauth, current_user
from app.models import User
import requests
import os

oauth_bp = Blueprint('oauth', __name__)

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={
                              'scope': 'https://www.googleapis.com/auth/userinfo.email',
                              'response_type': 'code'
                          },
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=os.environ['GOOGLE_CLIENT_ID'],
                          consumer_secret=os.environ['GOOGLE_CLIENT_SECRET'])

GOOGLE_OAUTH2_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


@oauth_bp.route('/oauth2callback')
@google.authorized_handler
def google_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_oauth_token'] = (resp['access_token'], '')
    userinfo = requests.get(GOOGLE_OAUTH2_USERINFO_URL, params=dict(
        access_token=resp['access_token'],
        )).json()

    user = User.query.filter_by(username=userinfo['email']).first()
    if not user:
        user = User(username=userinfo['email'], pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(
        'Logged in as id=%s name=%s' % (userinfo['id'], userinfo['name']),
        'success'
    )
    return redirect(url_for('frontend.index'))


@oauth_bp.route('/google-login')
def google_login():
    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('frontend.index'))
    return google.authorize(
        callback=url_for('oauth.google_authorized', _external=True))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_oauth_token')

# Twitter oauth ========================================

twitter = oauth.remote_app('twitter',
                           base_url='https://api.twitter.com/1.1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authenticate',
                           consumer_key='Twitter API Key',
                           consumer_secret='Twitter API Secret')

@oauth_bp.route('/twitter-login')
def twitter_login():
    return twitter.authorize(
        callback=url_for(
            'auth.twitter_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True
        ))


@oauth_bp.route('/twitter-login/authorized')
@twitter.authorized_handler
def twitter_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['twitter_oauth_token'] = resp['oauth_token'] + \
                                     resp['oauth_token_secret']

    user = User.query.filter_by(username=resp['screen_name']).first()
    if not user:
        user = User(resp['screen_name'], '')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Logged in as twitter handle=%s' % resp['screen_name'])
    return redirect(request.args.get('next'))


@twitter.tokengetter
def get_twitter_oauth_token():
    return session.get('twitter_oauth_token')

# Facebook ==================================

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key='FACEBOOK_APP_ID',
                            consumer_secret='FACEBOOK_APP_SECRET',
                            request_token_params={'scope': 'email'})

@oauth_bp.route('/facebook-login')
def facebook_login():
    return facebook.authorize(
        callback=url_for(
            'auth.facebook_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True
        ))


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
        user = User(me.data['email'], '')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(
        'Logged in as id=%s name=%s' % (me.data['id'], me.data['name']),
        'success'
    )
    return redirect(request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')