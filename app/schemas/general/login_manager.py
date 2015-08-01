from marshmallow import Schema


class LoginManagerSchema(Schema):
    """Data required by LoginManager.js to implement the client-side OAuth flow"""

    class Meta:
        # required fields
        fields = (
            'googleClientId', 'googleLoginUrl',
            'facebookClientId', 'facebookLoginUrl',
            'githubLoginUrl', 'logoutUrl',
            'loginUrl'
        )