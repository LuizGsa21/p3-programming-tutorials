import pprint
import os
import requests

from os.path import join as joinpath
from flask import Blueprint, request, redirect, url_for, flash, session, g, abort, render_template
from app.extensions import db, login_user, oauth, current_user, login_required
from app.models import User
from app.helpers.utils import xhr_required, format_flashed_messages
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

_oauthpath = os.path.dirname(os.path.realpath(__file__))


@oauth_bp.route('/google-authorized', methods=['POST'])
@xhr_required
def google_authorized():
    # CSRF is handled implicitly by flask_wtf.csrf (for post requests)

    if g.user and current_user.is_authenticated():
        flash('You are already logged in as %s. Please logout if this isn\'t you.' % current_user.username, 'warning')
        return {'status': 401, 'success': 0}
    # retrieve authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(joinpath(_oauthpath, 'google-secret.json'),
                                             scope='', redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        flash('Failed to upgrade authorization code.', 'danger')
        return {'status': 401, 'success': 0}
    access_token = credentials.access_token
    result = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo',
                          params={'access_token': access_token})
    # print 'verifying access token'
    # abort if access token is invalid
    if not result.ok:
        flash('Invalid access token.', 'danger')
        return {'status': result.status_code, 'success': 0}
    else:
        result = result.json()

    gplus_id = credentials.id_token['sub']
    # verify that the access token is used for the intended user
    if gplus_id != result['user_id']:
        flash("Token's user ID doesn't match given user ID.", 'danger')
        return {'status': 401, 'success': 0}

    # verify that the access token is valid for this app
    if result['issued_to'] != credentials.client_id:
        flash("Token's client ID does not match app's.", 'danger')
        return {'status': 401, 'success': 0}


    result = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params={'access_token': access_token})

    # abort if failed to retrieve user info
    if not result.ok:
        flash('Failed to retrieve user info.', 'danger')
        return {'status': result.status_code, 'success': 0}
    userinfo = result.json()
    user = User.query.filter_by(email_insensitive=userinfo['email']).first()
    isNewUser = user is None

    if isNewUser:
        user = User(username=userinfo['email'],
                    email=userinfo['email'],
                    first_name=userinfo.get('given_name', None),
                    last_name=userinfo.get('family_name', None),
                    oauth_id=gplus_id,
                    oauth_provider='google-plus',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()
    session['google_oauth_token'] = (access_token, '')
    login_user(user)
    msg = ''
    if isNewUser:
        msg = 'You have successfully registered!'
    flash(msg + 'You are logged in as %s' % user.username, 'success')

    return {'status': 200, 'success': 1}


@oauth_bp.route('/facebook-login/authorized', methods=['POST'])
@xhr_required
def facebook_authorized():

    if g.user and current_user.is_authenticated():
        flash('You are already logged in as %s. Please logout if this isn\'t you.' % current_user.username, 'warning')
        return {'status': 401, 'success': 0}

    accessToken = request.data

    params = {
        'client_id': os.environ['FACEBOOK_CLIENT_ID'],
        'client_secret': os.environ['FACEBOOK_CLIENT_SECRET'],
        'grant_type': 'fb_exchange_token',
        'fb_exchange_token': accessToken
    }

    result = requests.get('https://graph.facebook.com/oauth/access_token', params=params)

    if not result.ok:
        flash('Failed to exchange token.')
        return {'success': 0, 'status': 401}

    data = {s.split('=')[0]: s.split('=')[1] for s in result.text.split('&')}
    accessToken = data['access_token']
    result = requests.get('https://graph.facebook.com/v2.2/me', params={'access_token': accessToken})

    if not result.ok:
        flash('Failed to get user data.')
        return {'success': 0, 'status': 401}

    data = result.json()
    user = User.query.filter_by(email_insensitive=data['email']).first()

    if not user:
        user = User(username=data['email'],
                    email=data['email'],
                    first_name=data.get('first_name', None),
                    last_name=data.get('last_name', None),
                    oauth_id=data['id'],
                    oauth_provider='facebook',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)

    session['facebook_oauth_token'] = accessToken
    flash('Logged in as id=%s name=%s' % (data['id'], data['name']), 'success')

    return {'success': 1, 'status': 200}


github = oauth.remote_app('github', **{
    'base_url': 'https://api.github.com',
    'authorize_url': 'https://github.com/login/oauth/authorize',
    'request_token_url': None,
    'request_token_params': {
        'scope': 'user:email',
        },
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'access_token_method': 'POST',
    'consumer_key': os.environ.get('GITHUB_CLIENT_ID', None),
    'consumer_secret': os.environ.get('GITHUB_CLIENT_SECRET', None)
})

@oauth_bp.route('/github-login', methods=['POST'])
def github_login():
    # CSRF is handled implicitly by flask_wtf.csrf (for post requests)
    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('frontend.index'))
    return github.authorize(url_for('oauth.github_authorized', _external=True))

@oauth_bp.route('/github-authorized')
@github.authorized_handler
def github_authorized(resp):
    if resp is None:
        flash('Access denied.', 'danger')
        return render_template('close-popup.html')

    # get user info using github's api
    userinfo = requests.get('https://api.github.com/user',
                            params=dict(access_token=resp['access_token'])).json()

    # getting an email from github isn't guaranteed
    # so we use id provided by github
    user = User.query.filter_by(oauth_id=str(userinfo['id']), oauth_provider='github').first()
    if not user:

        fullname = userinfo['name'].split(' ', 1)
        if len(fullname) != 2:
            fullname = (fullname[0], None)
        firstname, lastname = fullname

        # check if github's username is available
        taken = User.query.filter_by(username=userinfo['login']).first()

        user = User(username=userinfo['login'] if not taken else userinfo['id'] + '-github',
                    email=userinfo['email'],
                    first_name=firstname,
                    last_name=lastname,
                    oauth_id=userinfo['id'],
                    oauth_provider='github',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()

    session['github_oauth_token'] = (resp['access_token'], '')
    login_user(user)
    flash('Logged in as %s' % user.username, 'success')
    result = {
        'flashed_messages': format_flashed_messages(),
        'success': 1
    }
    return render_template('close-popup.html', result=result)

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_oauth_token')