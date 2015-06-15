import os
from flask import current_app

providers = {
    'facebook': {
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_url': '/oauth/access_token',
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'consumer_key': os.environ.get('FACEBOOK_CLIENT_ID', None),
        'consumer_secret': os.environ.get('FACEBOOK_CLIENT_SECRET', None),
        'request_token_params': {'scope': 'email'}
    },
    'twitter': {
        'base_url': 'https://api.twitter.com/1.1/',
        'request_token_url': 'https://api.twitter.com/oauth/request_token',
        'access_token_url': 'https://api.twitter.com/oauth/access_token',
        'authorize_url': 'https://api.twitter.com/oauth/authorize',
        'consumer_key': os.environ.get('TWITTER_CLIENT_ID', None),
        'consumer_secret': os.environ.get('TWITTER_CLIENT_SECRET', None)
    },
    'github': {
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
    },
}