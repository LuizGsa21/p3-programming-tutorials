import os
from PIL import Image
from shutil import copyfile

from flask import Blueprint, render_template, request, flash, session, current_app, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import User, Article
from app.utils import xhr_required, get_login_manager_data, xhr_or_template
from app.models import Category, Article
from app.schemas import user_profile_view_serializer as profile_view_serializer, user_info_serializer
from app.forms import (
    AddArticleForm, EditArticleForm, DeleteArticleForm,
    AddCategoryForm, EditCategoryForm, DeleteCategoryForm,
    EditProfileForm, UploadAvatarForm,
    DeleteUserForm
)

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile/')
@login_required
@xhr_or_template('user/profile.html')
def profile():
    # Create response using `ProfileViewSchema`
    result = profile_view_serializer.dump({
        'user': current_user,
        'articles': Article.query.filter_by(authorId=current_user.id).order_by(func.lower(Article.title)).all(),
        'navbar': {
            'categories': Category.query.order_by(Category.name).all()
        }
    }).data

    return {'status': 200, 'result': result}

@user_bp.route('/profile/edit', methods=['POST'])
@xhr_required
def edit_profile():
    form = EditProfileForm(request.form)
    if form.validate_on_submit():
        # prevent non admin users from editing other users profile
        if not current_user.is_admin():
            form.id.data = current_user.id
        user = User.query.get(form.id.data)
        user.populate_from_form(form)
        db.session.commit()
        flash('Successfully updated user info.', 'success')
        return {'status': 200}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/articles/add', methods=['POST'])
@xhr_required
def add_article():
    form = AddArticleForm(request.form)
    if form.validate_on_submit():
        article = Article(authorId=current_user.id, **form.data)
        db.session.add(article)
        db.session.commit()
        flash("Successfully published <strong>'" + article.title + "'</strong>.", 'success')
        return {'status': 200}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/articles/edit', methods=['POST'])
@login_required
@xhr_required
def edit_article():
    form = EditArticleForm(request.form)
    if form.validate_on_submit():
        article = Article.query.get(form.id.data)
        # ensure user has permission to edit this article
        if article.authorId == current_user.id or current_user.is_admin():
            article.populate_from_form(form)
            db.session.commit()
            flash("Successfully updated <strong>'" + article.title + "'</strong> article.", 'success')
            return {'status': 200}
        else:
            flash('You do not have permission to edit <strong>' + article.title + '</strong>. article', 'danger')
            return {'status': 403}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/articles/delete', methods=['POST'])
@xhr_required
def delete_article():
    form = DeleteArticleForm(request.form)
    if form.validate_on_submit():
        article = Article.query.get(form.id.data)
        if not article:
            flash("This articles doesn't exist...", 'danger')
            return {'status': 400}
        # ensure the user has ownership before deleting the article
        if current_user.id == article.authorId or current_user.is_admin():
            db.session.delete(article)
            db.session.commit()
            flash("Successfully deleted <strong>'" + article.title + "'</strong> article.", 'success')
            return {'status': 200}
        else:
            flash('You do not have permission to delete <strong>' + article.title + '</strong>.', 'danger')
            return {'status': 403}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/categories/add', methods=['POST'])
@xhr_required
def add_category():
    if not current_user.is_admin():
        flash('Permission denied...', 'danger')
        return {'status': 403}

    form = AddCategoryForm(request.form)
    if form.validate_on_submit():
        category = Category(**form.data)
        db.session.add(category)
        db.session.commit()
        flash('Successfully added ' + category.name + '.', 'success')
        # return the updated navbar
        result = profile_view_serializer.dump({
            'navbar': {
                'categories': Category.query.order_by(Category.name).all()
            }
        }).data
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/categories/edit', methods=['POST'])
@xhr_required
def edit_category():
    if not current_user.is_admin():
        flash('Permission denied...', 'danger')
        return {'status': 403}

    form = EditCategoryForm(request.form)
    if form.validate_on_submit():
        category = Category.query.get(form.id.data)
        if not category:
            flash("This category doesn't exist...", 'danger')
            return {'status': 400}

        category.name = form.name.data
        db.session.commit()
        flash('Successfully updated ' + category.name + '.', 'success')
        # return the updated navbar
        result = profile_view_serializer.dump({
            'navbar': {
                'categories': Category.query.order_by(Category.name).all()
            }
        }).data
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@user_bp.route('/profile/categories/delete', methods=['POST'])
@xhr_required
def delete_category():
    if not current_user.is_admin():
        flash('Permission denied...', 'danger')
        return {'status': 403}

    form = DeleteCategoryForm(request.form)

    if form.validate_on_submit():
        category = Category.query.get(form.id.data)
        if category.articles.first():
            flash("You can't delete a category containing articles.", 'danger')
            return {'status': 400}
        name = category.name
        db.session.delete(category)
        db.session.commit()
        flash('Successfully deleted ' + name, 'success')
        # return the updated navbar
        result = profile_view_serializer.dump({
            'navbar': {
                'categories': Category.query.order_by(func.lower(Category.name)).all()
            }
        }).data
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}


@user_bp.route('/upload/avatar', methods=['POST'])
@xhr_required
def upload():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.avatar.data
        # avatar folder directory
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatar')
        # crop the provided image
        if image:
            # get the file extension.
            # Note: file extension was checked on form validation
            s = image.filename.rsplit('.', 1)

            # append user's id to filename
            filename = 'avatar-' + str(current_user.id) + '.' + s[1]
            # filename = secure_filename(filename)

            # get the paths used in `crop_image()`
            originalPath = os.path.join(path, 'original-' + filename)
            croppedPath = os.path.join(path, filename)

            # save the original image
            image.save(originalPath)
            image.close()
        else:
            # since no image was provided we will use the original image
            filename = current_user.avatar

            # create a file namespace if this is the user's first time editing his avatar
            if filename == 'avatar.jpg':
                filename = 'avatar-' + str(current_user.id) + '.jpg'
                copyfile(os.path.join(path, 'avatar.jpg'), os.path.join(path, filename))
                copyfile(os.path.join(path, 'original-avatar.jpg'), os.path.join(path, 'original-' + filename))

            # get the paths used in `crop_image()`
            originalPath = os.path.join(path, 'original-' + filename)
            croppedPath = os.path.join(path, filename)

        # create the cropped image
        crop_image(originalPath, croppedPath, form.cropData.data)

        # update user avatar path
        current_user.avatar = filename
        db.session.commit()
        flash('Successfully uploaded avatar image.', 'success')

        # return the new user avatar
        result = profile_view_serializer.dump({
            'user': current_user
        }).data

        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}


def crop_image(src, dst, size):
    original = Image.open(src)
    left = size['x']
    upper = size['y']
    right = left + size['width']
    lower = upper + size['height']
    cropped = original.crop((left, upper, right, lower))

    cropped.save(dst)
    cropped.close()

@user_bp.route('/profile/users/delete', methods=['POST'])
@xhr_required
def delete_user():
    if not current_user.is_admin():
        flash('Permission denied...', 'danger')
        return {'status': 403}
    form = DeleteUserForm(request.form)
    if form.validate_on_submit():
        if form.id.data == current_user.id:
            flash("You can't delete yourself. Find another admin user to do this for you.", 'danger')
            return {'status': 400}
        user = User.query.get(form.id.data)
        if not user:
            flash('Failed to delete non-existing user.')
            return {'status': 400}
        if user.articles.first():
            flash("You can't delete a user with published articles.", 'danger')
            return {'status': 400}
        db.session.delete(user)
        db.session.commit()
        return {'status': 200}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}