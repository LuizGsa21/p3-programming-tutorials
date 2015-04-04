from flask import Blueprint

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/profile/')
def profile():
    return 'profile'


@user.route('/settings/')
def settings():
    return 'settings'