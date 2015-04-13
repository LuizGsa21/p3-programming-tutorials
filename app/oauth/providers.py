import os


providers = {
    'google': {
        'base_url': 'https://www.google.com/accounts/',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'request_token_url': None,
        'request_token_params': {
            'scope': 'https://www.googleapis.com/auth/userinfo.email',
            'response_type': 'code'
        },
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'access_token_method': 'POST',
        'access_token_params': {'grant_type': 'authorization_code'},
        'consumer_key': os.environ['GOOGLE_CLIENT_ID'],
        'consumer_secret': os.environ['GOOGLE_CLIENT_SECRET']
    },

    'facebook': {
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_url': '/oauth/access_token',
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'consumer_key': os.environ['FACEBOOK_CLIENT_ID'],
        'consumer_secret': os.environ['FACEBOOK_CLIENT_SECRET'],
        'request_token_params': {'scope': 'email'}
    },

    'twitter': {
        'base_url': 'https://api.twitter.com/1.1/',
        'request_token_url': 'https://api.twitter.com/oauth/request_token',
        'access_token_url': 'https://api.twitter.com/oauth/access_token',
        'authorize_url': 'https://api.twitter.com/oauth/authorize',
        'consumer_key': os.environ['TWITTER_CLIENT_ID'],
        'consumer_secret': os.environ['TWITTER_CLIENT_SECRET']
    }
}