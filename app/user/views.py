from flask import Blueprint, render_template, g, url_for, redirect, request, flash
from app.extensions import current_user, login_required, db
from app.models import User, Article
from app.utils import template_or_json, redirect_or_json
from .schemas import articles_serializer, user_info_serializer
from .forms import AddArticleForm, DeleteArticleForm, EditArticleForm, EditProfileForm

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile/')
@login_required
def profile():
    forms = {
        'addArticle': AddArticleForm(),
        'deleteArticle': DeleteArticleForm(),
        'editProfile': DeleteArticleForm()
    }
    serializers = {
        'article': articles_serializer,
        'userInfo': user_info_serializer
    }
    return render_template('user/profile.html', active_page='profile', forms=forms, serializers=serializers)

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
        flash("Successfully added <strong>'" + article.title + "'</strong> tutorial.", 'success')
        result, error = article_serializer.dump(article)
        return {'status': 200, 'article': result, 'success': 1}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400, 'success': 0}

@user_bp.route('/profile/articles/edit', methods=['POST'])
@redirect_or_json('user.profile')
def edit_article():
    form = EditArticleForm(request.form)
    if form.validate_on_submit():
        article = Article.query.get(form.id.data)
        # ensure user has permission to edit this item
        if article.author_id == current_user.id or current_user.isAdmin():
            article.title = form.title.data
            article.body = form.body.data
            article.category_id = form.category.data.id
            db.session.commit()
            flash("Successfully updated <strong>'" + article.title + "'</strong> tutorial.", 'success')
            result, error = article_serializer.dump(article)
            return {'status': 200, 'success': 1, 'article': result}
        else:
            flash('You do not have permission to edit <strong>' + article.title + '</strong>. tutorial', 'danger')
            return {'status': 403, 'success': 0}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400, 'success': 0}

@user_bp.route('/profile/articles/delete', methods=['POST'])
@redirect_or_json('user.profile')
def delete_article():
    form = DeleteArticleForm(request.form)
    if form.validate_on_submit():
        article = Article.query.get(form.id.data)
        title = article.title
        # ensure the user has ownership before deleting the article
        if current_user.id == article.author_id:
            db.session.delete(article)
            db.session.commit()
            flash("Successfully deleted <strong>'" + article.title + "'</strong> tutorial.", 'success')
            return {'status': 200, 'success': 1}
        else:
            flash('You do not have permission to delete <strong>' + title + '</strong>.', 'danger')
            return {'status': 403, 'success': 0}
    else:
        flash('Invalid tutorial identification number.', 'danger')
        return {'status': 400, 'success': 0}

@user_bp.route('/profile/settings/edit', methods=['POST'])
@redirect_or_json('user.profile')
def edit_profile():
    form = EditProfileForm(request.form)
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.email = form.email.data


@user_bp.route('/settings/')
def settings():
    return 'settings'
