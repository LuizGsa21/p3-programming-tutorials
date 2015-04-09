from flask import Blueprint

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile/')
def profile():
    return 'profile'


@user_bp.route('/settings/')
def settings():
    return 'settings'