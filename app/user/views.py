import os
from flask import Blueprint, render_template, request, flash, session, current_app
from werkzeug import secure_filename
from app.extensions import current_user, login_required, db
from app.models import User, Article
from app.helpers.utils import xhr_required
from app.api.schemas import articles_serializer, article_serializer
from .schemas import user_info_serializer
from .forms import AddArticleForm, DeleteArticleForm, EditArticleForm, EditProfileForm, UploadAvatarForm

user_bp = Blueprint('user', __name__, url_prefix='/user')
# TODO: update all `current_user` views to use `current_user`


@user_bp.route('/profile/')
@login_required
def profile():
    forms = {
        'addArticle': AddArticleForm(),
        'deleteArticle': DeleteArticleForm(),
        'editProfile': EditProfileForm(),
        'uploadAvatarForm': UploadAvatarForm()
    }

    serializers = {
        'article': articles_serializer,
        'userInfo': user_info_serializer
    }

    return render_template('user/profile.html', active_page='profile', forms=forms, serializers=serializers)

@user_bp.route('/profile/articles/add', methods=['POST', 'GET'])
@xhr_required
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
        flash("Successfully published <strong>'" + article.title + "'</strong>.", 'success')
        result, error = article_serializer.dump(article)
        return {'status': 200, 'article': result, 'success': 1}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400, 'success': 0}

@user_bp.route('/profile/articles/edit', methods=['POST'])
@xhr_required
def edit_article():
    form = EditArticleForm(request.form)
    if form.validate_on_submit():
        article = Article.query.get(form.id.data)
        # ensure user has permission to edit this item
        if article.author_id == current_user.id or current_user.is_admin():
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
@xhr_required
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
@xhr_required
def edit_profile():

    form = EditProfileForm(request.form)

    if form.validate_on_submit():
        user = User.query.get(current_user.id)

        # Users who registered using OAuth may only change their username once.
        if form.username.data != user.username:
            session.pop('change-username', None)

        user.populate_form(form)
        db.session.commit()

        flash('Successfully updated user info.', 'success')
        result, error = user_info_serializer.dump(user)
        return {'status': 200, 'success': 1, 'userInfo': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400, 'success': 0}


@user_bp.route('/upload/avatar', methods=['POST'])
@xhr_required
def upload():
    # there's no need to pass the form. WTF already takes care of it for file uploads
    form = UploadAvatarForm()

    if form.validate_on_submit():
        avatar = form.avatar.data

        # append user id to filename (creates a file namespace)
        s = avatar.filename.rsplit('.', 1)
        filename = s[0] + str(current_user.id) + '.' + s[1]

        # filter user input
        filename = secure_filename(filename)
        avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', filename))

        # update user avatar path
        current_user.avatar = filename
        db.session.commit()
        flash('Successfully uploaded avatar image.', 'success')

        result, error = user_info_serializer.dump(current_user._get_current_object())

        return {'status': 200, 'success': 1, 'userInfo': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400, 'success': 0}