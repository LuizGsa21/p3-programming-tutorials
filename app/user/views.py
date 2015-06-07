from flask import Blueprint, render_template, g, url_for, redirect, request, flash
from app.models import User, Article
from app.extensions import current_user, login_required, db
from .forms import AddArticleForm
from app.utils import template_or_json, redirect_or_json
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile/')
@login_required
def profile():
    test = current_user.articles
    print test.all()

    return render_template('user/profile.html', active_page='profile', form=AddArticleForm())

@user_bp.route('/profile/articles/add', methods=['POST'])
@redirect_or_json('user.profile')
def add_article():
    form = AddArticleForm(request.form)
    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            body=form.body.data,
            author_id=current_user.id,
            category_id=form.category.data.id)
        db.session.add(article)
        db.session.commit()
        flash('successfully added article', 'success')
        return {'status': 200, 'article': article.serialize()}
    else:
        flash(form.errors, 'danger')
        return {'status': 400, 'error': form.errors}

@user_bp.route('/settings/')
def settings():
    return 'settings'
