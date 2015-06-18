import os
from os.path import join as joinpath
import pprint

from flask import Blueprint, request, redirect, url_for, flash, session, g, abort, render_template, jsonify
import requests

from app.extensions import db, login_user, oauth, current_user
from app.models import User
from app.helpers.utils import xhr_required
from providers import providers

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

facebook = oauth.remote_app('facebook', **providers['facebook'])
github = oauth.remote_app('twitter', **providers['github'])
twitter = oauth.remote_app('github', **providers['twitter'])

remote_apps = oauth.remote_apps

_oauthpath = os.path.dirname(os.path.realpath(__file__))


@oauth_bp.route('/<provider>-login', methods=['POST'])
def oauth_login(provider):
    # CSRF is handled implicitly by flask_wtf.csrf (for post requests)

    if provider not in remote_apps.keys():
        abort(404)

    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return render_template('close-popup.html')

    return remote_apps[provider].authorize(url_for('oauth.%s_authorized' % provider, _external=True))


# @google.authorized_handler
@oauth_bp.route('/google-authorized', methods=['POST'])
@xhr_required
def google_authorized():
    # CSRF is handled implicitly by flask_wtf.csrf (for post requests)

    # retrieve authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(joinpath(_oauthpath, 'google-secret.json'), scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return jsonify({'error':'Failed to upgrade the authorization code.'}), 401

    # check that the access token is valid
    access_token = credentials.access_token
    result = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo',
                          params={'access_token':access_token})
    # abort if access token is invalid
    if not result.ok:
        return jsonify(result.json()), result.status_code
    else:
        result = result.json()

    gplus_id = credentials.id_token['sub']
    # verify that the access token is used for the intended user
    if gplus_id != result['user_id']:
        return jsonify({'error':"Token's user ID doesn't match given user ID."}), 401

    # verify that the access token is valid for this app
    if result['issued_to'] != credentials.client_id:
        return jsonify({'error': "Token's client ID does not match app's."}), 401


    result = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                            params={'access_token':access_token})
    userinfo = result.json()
    # abort if failed to retrieve user info
    if not result.ok:
        return jsonify(userinfo), result.status_code

    user = User.query.filter_by(email_insensitive=userinfo['email']).first()

    print user

    if not user:
        user = User(username=userinfo['email'],
                    email=userinfo['email'],
                    first_name=userinfo.get('given_name', ''),
                    last_name=userinfo.get('family_name', ''),
                    oauth_id=gplus_id,
                    oauth_provider='google-plus',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()
    session['google_oauth_token'] = (access_token, '')
    login_user(user)
    flash('Logged in as id=%s name=%s' % (userinfo['id'], userinfo['name']), 'success')
    return {'status': 200, 'success': 1}



@oauth_bp.route('/facebook-login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash('Access denied.', 'danger')
        return render_template('close-popup.html')

    session['facebook_oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    user = User.query.filter_by(email_insensitive=me.data['email']).first()
    pprint.pprint(me.data)
    if not user:
        user = User(username=me.data['email'],
                    email=me.data['email'],
                    first_name=me.data.get('first_name', None),
                    last_name=me.data.get('last_name', None),
                    pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Logged in as id=%s name=%s' % (me.data['id'], me.data['name']), 'success')
    return render_template('close-popup.html')



@oauth_bp.route('/github-authorized')
@github.authorized_handler
def github_authorized(resp):
    pprint.pprint(request.args)
    pprint.pprint(resp)
    pprint.pprint(session)
    if resp is None:
        flash('Access denied.', 'danger')
        return render_template('close-popup.html')

    # get user info using github's api
    userinfo = requests.get('https://api.github.com/user',
                            params=dict(access_token=resp['access_token'])).json()

    # getting an email from github isn't guaranteed
    # so we use id provided by github
    user = User.query.filter_by(oauth_id=userinfo['id'], oauth_type='github').first()
    if not user:

        # extract first and last name. ('firstname', 'lastname')
        fullname = userinfo['name'].partition(' ')[0:3:2]

        # check if github's username is taken by another user
        exists = User.query.filter_by(username=userinfo['login']).first()

        # use the id provided by github if the username name is take and append `-github` to it.
        user = User(username=userinfo['login'] if not exists else userinfo['id'] + '-github',
                    email=userinfo['email'],
                    first_name=fullname[0],
                    last_name=fullname[2],
                    oauth_id=userinfo['id'],
                    oauth_type='github',
                    pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Logged in as github handle=%s' % user.username, 'success')
    return redirect(url_for('oauth.close_popup'))

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_oauth_token')

# @google.tokengetter
# def get_google_oauth_token():
#     return session.get('google_oauth_token')


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')

@oauth_bp.route('/redirect')
def close_popup():
    return render_template('close-popup.html')