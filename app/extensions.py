from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_wtf import CsrfProtect
csrf = CsrfProtect()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_openid import OpenID
oid = OpenID()

