from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.extensions import db, login_manager, current_user, login_user, logout_user, login_required, oid, oauth
from forms import LoginForm, RegistrationForm, OpenIDForm
from app.models import User
import requests

frontend = Blueprint('frontend', __name__)

login_manager.login_view = 'frontend.login'


@frontend.route('/')
def index():
    return render_template('frontend/index.html')


@frontend.route('/login/', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if not g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('frontend.index'))
    form = LoginForm(request.form)
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        if openid_form.errors:
            flash(openid_form.errors, 'danger')
            return render_template('frontend/login.html', form=form, openid_form=openid_form)
        openid = request.form.get('openid')
        return oid.try_login(openid, ask_for=['email'])

    elif form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter(User.username_insensitive == username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password. Please try again.', 'danger')
        else:
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('frontend.index'))

    return render_template('frontend/login.html', form=form, openid_form=openid_form)


@frontend.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.username.data, pwdhash=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered.', 'success')
        return redirect(url_for('frontend.index'))
    return render_template('frontend/register.html', form=form)


@oid.after_login
def after_login(response):
    username = response.email
    if not username:
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('frontend.login'))

    user = User.query.filter_by(username=username).first()
    # create a new user if username isn't registered
    if not user:
        user = User(username=username, pwdhash='')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Welcome %s you have successfully logged in.' % username, 'success')
    return redirect(url_for('frontend.index'))


@frontend.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('frontend.index'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

