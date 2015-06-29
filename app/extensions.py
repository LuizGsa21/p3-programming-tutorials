from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_wtf import CsrfProtect, Form
csrf = CsrfProtect()

from flask_login import LoginManager, current_user, login_user, logout_user, login_required
login_manager = LoginManager()

# from flask_openid import OpenID
# oid = OpenID()

from flask_oauth import OAuth
oauth = OAuth()

# from flask_mail import Mail, Message
# mail = Mail()

from flask_babel import Babel, format_datetime
babel = Babel()