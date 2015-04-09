import os


class Config(object):
    PROJECT = 'How-To-Tutorials'
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    PROJECT_TEMPLATES = os.path.join(PROJECT_ROOT, 'templates')
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ECHO = False
    ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
    LOGIN_DISABLED = False


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'how-to-tutorials-development'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    # SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    SECRET_KEY = 'how-to-tutorials-development'
    TESTING = True
    WTF_CSRF_ENABLED = False
    # SQLALCHEMY_ECHO = True
