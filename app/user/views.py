from flask import Blueprint, render_template, g, url_for, redirect, request, flash
from app.models import User, Article
from app.extensions import current_user, login_required, db
from .forms import AddArticleForm
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile/')
@login_required
def profile():
    return render_template('user/profile.html', active_page='profile', form=AddArticleForm())

@user_bp.route('/profile/articles/add', methods=['POST'])
def add_article():
    form = AddArticleForm(request.form)
    if form.validate_on_submit():
        db.session.add(Article(
            title=form.title.data,
            body=form.body.data,
            author_id=form.title.data,
            category_id=form.title.data))
        db.session.commit()
        flash('successfully added article', 'success')
    else:
        flash(form.errors, 'danger')
    return redirect(url_for('user.profile'))
@user_bp.route('/settings/')
def settings():
    return 'settings'
