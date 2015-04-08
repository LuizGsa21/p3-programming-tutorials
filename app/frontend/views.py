from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.extensions import db, login_manager, current_user, login_user, logout_user, login_required
from forms import LoginForm, RegistrationForm
from app.models import User

frontend = Blueprint('frontend', __name__)

login_manager.login_view = 'frontend.login'


@frontend.route('/')
def index():
    return render_template('frontend/index.html')


@frontend.route('/login/', methods=['GET', 'POST'])
def login():
    if not g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('frontend.index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter(User.username_insensitive == username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password. Please try again.', 'danger')
        else:
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('frontend.index'))

    return render_template('frontend/login.html', form=form)


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


@frontend.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('frontend.index'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

