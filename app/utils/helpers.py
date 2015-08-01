import os
from flask import url_for, get_flashed_messages


def format_flashed_messages():
    return [{'category': c, 'message': m} for c, m in get_flashed_messages(with_categories=True)]


def get_login_manager_data(cache=True):
    # only initialize on first call
    if not cache or not hasattr(get_login_manager_data, 'data'):
        data = {
            'googleClientId': os.environ['GOOGLE_CLIENT_ID'],
            'googleLoginUrl': url_for('oauth.google_authorized'),
            'facebookClientId': os.environ['FACEBOOK_CLIENT_ID'],
            'facebookLoginUrl': url_for('oauth.facebook_authorized'),
            'logoutUrl': url_for('frontend.logout'),
            'loginUrl': url_for('frontend.login'),
            # We don't need to share github's client id
            # because we will implementing a full server-side flow
            'githubLoginUrl': url_for("oauth.github_login", _external=True)
        }
        get_login_manager_data.data = data
    return get_login_manager_data.data