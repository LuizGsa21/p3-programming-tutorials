from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_wtf import CsrfProtect
csrf = CsrfProtect()

from flask_login import LoginManager, current_user, login_user, logout_user, login_required
login_manager = LoginManager()

from flask_openid import OpenID
oid = OpenID()

