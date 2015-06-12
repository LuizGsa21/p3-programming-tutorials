import os


class Config(object):
    PROJECT = 'How-To-Tutorials'

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
    TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ECHO = False

    ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
    UPLOAD_FOLDER =  os.path.join(STATIC_FOLDER, 'uploads')
    MAX_UPLOAD_SIZE = 500*1024^2 # about 500KB

    LOGIN_DISABLED = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'how-to-tutorials-development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    # SQLALCHEMY_ECHO = True
    # EMAIL SETTINGS
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ['MAIL_USERNAME']
    # MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    # MAIL_DEFAULT_SENDER = os.environ['MAIL_SENDER']


class TestingConfig(Config):
    SECRET_KEY = 'how-to-tutorials-development'
    TESTING = True
    # WTF_CSRF_ENABLED = False
    # SQLALCHEMY_ECHO = True
