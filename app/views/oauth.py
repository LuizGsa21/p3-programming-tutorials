import os
from os.path import join as joinpath

import requests
from flask import Blueprint, request, redirect, url_for, flash, session, g, render_template
from flask_login import login_user, current_user, login_required

from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

from app.extensions import db, oauth
from app.models import User, Category
from app.utils import xhr_required, format_flashed_messages, xhr_or_template, get_login_manager_data
from app.schemas import user_info_serializer, navbar_serializer, login_manager_serializer
from app.forms import RegisterUsernameForm


oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

_json_path = os.getcwd()


@oauth_bp.route('/google-authorized', methods=['POST'])
@xhr_required
def google_authorized():
    # CSRF is handled implicitly by flask_wtf.csrf (for post requests)

    if g.user and current_user.is_authenticated():
        flash('You are already logged in as %s.' % current_user.username, 'warning')
        return {'status': 401}
    # retrieve authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(joinpath(_json_path, 'google-secret.json'),
                                             scope='', redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        flash('Failed to upgrade authorization code.', 'danger')
        return {'status': 401}
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
        return {'status': 401}

    # verify that the access token is valid for this app
    if result['issued_to'] != credentials.client_id:
        flash("Token's client ID does not match app's.", 'danger')
        return {'status': 401}


    result = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params={'access_token': access_token})

    # abort if failed to retrieve user info
    if not result.ok:
        flash('Failed to retrieve user info.', 'danger')
        return {'status': result.status_code}
    userinfo = result.json()

    # check if user exists
    user = User.query.filter_by(oauthId=gplus_id, oauthProvider='google-plus').first()
    if not user:
        # use a temporary username. As long as the username contains a `@`
        # the user will be redirected to `register_username` endpoint
        user = User(username=gplus_id + '@google',
                    email=userinfo['email'],
                    firstName=userinfo.get('given_name', None),
                    lastName=userinfo.get('family_name', None),
                    oauthId=gplus_id,
                    oauthProvider='google-plus',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    session['google_oauth_token'] = (access_token, '')
    result = {
        'user': user_info_serializer.dump(user).data,
    }
    return {'status': 200, 'result': result}


@oauth_bp.route('/facebook-login/authorized', methods=['POST'])
@xhr_required
def facebook_authorized():

    if g.user and current_user.is_authenticated():
        flash('You are already logged in as %s.' % current_user.username, 'warning')
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
    # check if user exists
    user = User.query.filter_by(oauthId=data['id'], oauthProvider='facebook').first()
    if not user:
        # use a temporary username. As long as the username contains a `@`
        # the user will be redirected to `register_username` endpoint
        user = User(username=data['id'] + '@facebook',
                    email=data['email'],
                    firstName=data.get('first_name', None),
                    lastName=data.get('last_name', None),
                    oauthId=data['id'],
                    oauthProvider='facebook',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()
    login_user(user)

    session['facebook_oauth_token'] = accessToken
    result = {
        'user': user_info_serializer.dump(user).data,
    }
    return {'status': 200, 'result': result}


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
        result = {
            'flashed_messages': format_flashed_messages(),
            'success': 0
        }
        return render_template('close-popup.html', result=result)

    # get user info using github's api
    userinfo = requests.get('https://api.github.com/user',
                            params=dict(access_token=resp['access_token'])).json()

    # check if user exists
    user = User.query.filter_by(oauthId=str(userinfo['id']), oauthProvider='github').first()
    if not user:
        # get first and last name if possible.
        fullname = userinfo['name'].split(' ', 1)
        if len(fullname) != 2:
            fullname = (fullname[0], None)
        firstname, lastname = fullname

        # use a temporary username. As long as the username contains a `@`
        # the user will be redirected to `register_username` endpoint
        user = User(username=str(userinfo['id']) + '@github',
                    email=userinfo['email'],
                    firstName=firstname,
                    lastName=lastname,
                    oauthId=userinfo['id'],
                    oauthProvider='github',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()
    session['github_oauth_token'] = (resp['access_token'], '')
    login_user(user)
    result = {
        'flashed_messages': format_flashed_messages(),
        'user': user_info_serializer.dump(user).data,
        'success': 1
    }
    return render_template('close-popup.html', result=result)

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_oauth_token')

@oauth_bp.route('/register-username', methods=['POST', 'GET'])
@login_required
@xhr_or_template('oauth/register-username.html')
def register_username():
    print request.form
    result = {
        'navbar': navbar_serializer.dump({
            'categories': Category.query.order_by(Category.name).all()
        }).data,
        'loginManager': login_manager_serializer.dump(get_login_manager_data()).data
    }

    # only register a new username if it contains a "@"
    if '@' not in current_user.username:
        flash('You already have a username.', 'danger')
        if not request.is_xhr:
            # redirect back to the home page
            return redirect(url_for('frontend.index'))
        return {'status': 400}

    # validate the form on post requests
    if request.method == 'POST':
        form = RegisterUsernameForm(request.form, prefix='cr')
        if form.validate_on_submit():
            # Update username
            user = User.query.get(current_user.id)
            user.populate_from_form(form)
            db.session.commit()

            flash('Welcome ' + user.username + ' :)', 'success')
            # create response
            result['user'] = user_info_serializer.dump(current_user).data
            response = {'status': 200, 'result': result}
            # Check if we should delay the flash message
            print request.form['delay-flash-messages']
            if request.form['delay-flash-messages']:
                response['_delayFlashMessages'] = True
            return response
        else:
            # return form errors
            flash(form.errors, 'form-error')
            return {'status': 400}
    else:
        # create response
        result['user'] = user_info_serializer.dump(current_user).data
        flash('You must register a username or logout to continue.', 'danger')
        if request.is_xhr:
            # xhr request should not be using GET with this endpoint
            return {'status': 400}
        else:
            return {'status': 200, 'result': result}