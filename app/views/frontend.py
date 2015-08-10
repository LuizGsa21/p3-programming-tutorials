from datetime import datetime
import pprint
from sqlalchemy import type_coerce, Integer, or_
from sqlalchemy import DateTime, cast

from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import literal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db, login_manager
from app.utils import xhr_or_redirect, xhr_required, get_login_manager_data, xhr_or_template
from app.forms import LoginForm, RegisterForm, AddCommentForm, AddReplyForm, EditCommentForm, EditReplyForm
from app.models import User, Article, Category, Comment
from app.schemas import (
    frontend_article_view_serializer as article_view_serializer,
    frontend_index_view_serializer as index_view_serializer,
    frontend_category_articles_serializer as category_articles_serializer,
    user_info_serializer
)
# JSON schema views

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
@xhr_or_template('frontend/index.html')
def index():
    # Create response using `IndexViewSchema`
    result = index_view_serializer.dump({
        'user': current_user,
        'loginManager': get_login_manager_data(),
        'navbar': {
            'categories': Category.query.order_by(Category.name).all()
        }
    }).data

    return {'status': 200, 'result': result}


@frontend_bp.route('/<category>/')
@xhr_or_template('frontend/articles.html')
def category_articles(category):
    category = Category.query.filter_by(name=category).first()
    # Check if exists
    if category is None:
        abort(404)
    # Create response using `CategoryArticlesViewSchema`
    result = category_articles_serializer.dump({
        'user': current_user,
        'category': category.name,
        'loginManager': get_login_manager_data(),
        'articles': category.articles.order_by(Article.dateCreated).all(),
        'navbar': {
            'categories': Category.query.order_by(Category.name).all()
        }
    }).data

    return {'status': 200, 'result': result}


@frontend_bp.route('/<category>/<int:articleId>/<title>')
@xhr_or_template('frontend/article.html')
def article(category, articleId, title):
    article = Article.query.get(articleId)
    # Check if article exists
    if not article:
        abort(404)
    # redirect if the category or title doesn't match the article
    if article.title != title or category != article.category.name:
        return redirect(url_for('.article', category=article.category.name, articleId=article.id, title=article.title))

    comments = get_comments(articleId)
    # Create response using `ArticleViewSchema`
    result = article_view_serializer.dump({
        'user': current_user,
        'article': article,
        'comments': comments,
        'loginManager': get_login_manager_data(),
        'navbar': {
            'categories': Category.query.order_by(Category.name).all()
        }
    }).data
    return {'status': 200, 'result': result}



@frontend_bp.route('/add/comment', methods=['POST'])
@login_required
@xhr_required
def add_comment():
    form = AddCommentForm(request.form)
    # validate the form
    if form.validate_on_submit():
        comment = Comment(userId=current_user.id, **form.data)
        db.session.add(comment)
        db.session.commit()
        result = {
            'comments': get_comments(comment.articleId)
        }
        result, error = article_view_serializer.dump(result)
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}

@frontend_bp.route('/add/reply', methods=['POST'])
@login_required
@xhr_required
def add_reply():
    form = AddReplyForm(request.form)
    # validate the form
    if form.validate_on_submit():
        recipient = Comment.query.get(form.parentId.data)
        # Make sure the recipient isn't a deleted user
        if recipient.user is None:
            flash("You can't reply to a non-existing user.", 'danger')
            return {'status': 400}
        comment = Comment(userId=current_user.id, **form.data)
        db.session.add(comment)
        db.session.commit()
        result = {
            'comments': get_comments(comment.articleId)
        }
        result, error = article_view_serializer.dump(result)
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}


@frontend_bp.route('/edit/comment', methods=['POST'])
@login_required
@xhr_required
def edit_comment():
    # find out the form type
    if request.form.get('subject', None) is None:
        form = EditReplyForm(request.form)
    else:
        form = EditCommentForm(request.form)

    # validate the form
    if form.validate_on_submit():

        comment = Comment.query.filter_by(id=form.id.data).first()
        if comment is None:
            flash('No comment found.')
            return {'success': 0, 'status': 401}
        if comment.userId != current_user.id:
            flash('You do not have permission to edit this comment.')
            return {'success': 0, 'status': 401}

        comment.populate_from_form(form)
        comment.lastModified = datetime.utcnow()
        db.session.commit()
        result = {
            'comments': get_comments(comment.articleId)
        }
        result, error = article_view_serializer.dump(result)
        return {'status': 200, 'result': result}
    else:
        flash(form.errors, 'form-error')
        return {'status': 401}


# @frontend_bp.route('/mail/')
# def send_mail():
#     msg = Message('Hello its luiz :)',
#                   body='this is an email. lol',
#                   recipients=['larantessa@icloud.com'])
#     mail.send(msg)
#     return redirect(url_for('frontend.index'))


@frontend_bp.route('/login/', methods=['POST'])
@xhr_required
def login():
    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return {'status': 400}

    form = LoginForm(request.form, prefix='l')
    if form.validate_on_submit():
        emailOrUsername = form.email.data
        if '@' in emailOrUsername:
            user = User.query.filter(User.email_insensitive == emailOrUsername).first()
        else:
            user = User.query.filter(User.username_insensitive == emailOrUsername).first()

        password = form.password.data
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return {'status': 400}
        else:
            login_user(user)
            flash('You have successfully logged in.', 'success')
            result = {'user': user_info_serializer.dump(user).data}
            return {'status': 200, 'result': result}

    flash(form.errors, 'form-error')
    return {'status': 400}


@frontend_bp.route('/register/', methods=['POST'])
@xhr_required
def register():
    if g.user and current_user.is_authenticated():
        flash('You are currently logged in as ' + current_user.username + '. If this isn\'t you please logout.',
              'warning')
        return redirect(url_for('frontend.index'))

    form = RegisterForm(request.form, prefix='r')
    if form.validate_on_submit():
        # register and login user
        user = User(
            username=form.username.data,
            email=form.email.data,
            pwdhash=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('You have successfully registered. <br> You are currently logged in as <strong>' + user.username + '</strong>.', 'success')
        return {'status': 200, 'result': {'user': user_info_serializer.dump(user).data}}
    else:
        flash(form.errors, 'form-error')
        return {'status': 400}


@frontend_bp.route('/logout/', methods=['GET', 'POST'])
@xhr_or_redirect('frontend.index')
def logout():
    if not current_user.is_authenticated():
        flash('You must be logged in to logout...', 'warning')
        return {'status': 401, 'success': 0}
    logout_user()
    flash('You have successfully logged out.', 'success')
    return {'status': 200}


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
@xhr_or_redirect('frontend.index')
def unauthorized():
    flash('You are not logged in.', 'danger')
    return {'status': 401}

def get_comments(articleId):
    # TODO: Test if using 2 CTEs is faster than 1. Revert back to 1 CTE if it isn't :/
    cte1 = db.session.query(Comment,
                            array([Comment.id]).label('path'),
                            literal(0, type_=Integer).label('depth')
                            ) \
        .filter_by(articleId=articleId, parentId=None).cte(name='cte', recursive=True)
    # Get all comments by article id and save it to a cte
    cte2 = db.session.query(Comment) \
        .filter_by(articleId=articleId).cte(name='cte2', recursive=False)

    c1_alias = aliased(cte1, name='c1')
    c2_alias = aliased(cte2, name='c2')

    cte1 = cte1.union_all(
        db.session.query(c2_alias,
                         c1_alias.c.path + array([c2_alias.c.id]).label('path'),
                         c1_alias.c.depth + literal(1, type_=Integer).label('depth'))
            .join(c1_alias, c2_alias.c.parentId == c1_alias.c.id))

    result = db.session.query(Comment,
                              type_coerce(cte1.c.path, ARRAY(Integer, as_tuple=True)),
                              cte1.c.depth
                              ). \
        select_entity_from(cte1).order_by('path').all()
    comments = []
    for comment, path, depth in result:
        comments.append(comment)
    return comments
