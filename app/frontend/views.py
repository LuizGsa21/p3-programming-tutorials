import pprint
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import array
from app.extensions import db, login_manager, current_user, login_user, \
    logout_user, login_required, oauth
from app.helpers.utils import xhr_required, format_flashed_messages, xhr_or_redirect
from forms import LoginForm, RegisterForm, AddCommentForm, ReplyForm
from sqlalchemy.dialects.postgresql import ARRAY
from app.models import User, Article, Category, Comment
from sqlalchemy import type_coerce, Integer, or_
from sqlalchemy.sql.expression import literal
from app.api.schemas import comments_nested_serializer, user_serializer
from sqlalchemy import DateTime, cast
frontend_bp = Blueprint('frontend', __name__)

login_manager.login_view = 'frontend.login'


@frontend_bp.route('/')
def index():
    forms = {'register': RegisterForm(prefix='r'), 'login': LoginForm(prefix='l')}

    return render_template('frontend/index.html', forms=forms)


@frontend_bp.route('/<category>/')
def category_articles(category):
    category = Category.query.filter_by(name=category).first()
    if category is None:
        abort(404)

    articles = category.articles
    # TODO: order articles by most popular
    page_articles = {
        'latest': articles.order_by(Article.date_created).all()
        # 'popular': articles.join(Comment)
    }
    return render_template('frontend/tutorials.html', active_page=category, articles=page_articles)


@frontend_bp.route('/<category>/<int:article_id>/<title>')
def article(category, article_id, title):
    article = Article.query.get(article_id)

    cte1 = db.session.query(Comment,
                           array([Comment.id]).label('path'),
                           literal(0, type_=Integer).label('depth')
                           ) \
        .filter_by(article_id=article_id, parent_id=None) \
        .cte(name='cte', recursive=True)
    cte2 = db.session.query(Comment).filter_by(article_id=article_id).cte(name='cte2', recursive=False)
    c1_alias = aliased(cte1, name='c1')
    c2_alias = aliased(cte2, name='c2')

    cte1 = cte1.union_all(
        db.session.query(c2_alias,
                         c1_alias.c.path + array([c2_alias.c.id]).label('path'),
                         c1_alias.c.depth + literal(1, type_=Integer).label('depth'))
            .join(c1_alias, c2_alias.c.parent_id == c1_alias.c.id))

    result = db.session.query(Comment,
                              type_coerce(cte1.c.path, ARRAY(Integer, as_tuple=True)),
                              cte1.c.depth
                              ). \
        select_entity_from(cte1).order_by('path').all()
    forms = {
        'addCommentForm': AddCommentForm(article_id=article.id),
        'replyForm': ReplyForm(article_id=article.id),
        'register': RegisterForm(prefix='r'),
        'login': LoginForm(prefix='l')
    }

    parents = []  # comments referring to the article.
    children = []  # comments referring to other comments
    for comment, path, depth in result:
        if depth == 0:  # if its a parent
            children = []
            parents.append((comment, depth, children))
        else:
            children.append((comment, depth, None))

    return render_template('frontend/tutorial.html', comments=parents, article=article, forms=forms)


@frontend_bp.route('/add/comment', methods=['POST'])
@login_required
@xhr_required
def add_comment():

    # find out the form type
    if request.form.get('parent_id', None) is None:
        form = AddCommentForm(request.form)
    else:
        form = ReplyForm(request.form)

    # a timestamp telling us the latest comment loaded on the user's page
    lastmodified = request.form.get('lastmodified', None)

    # validate the form
    if form.validate_on_submit():

        comment = Comment(user_id=current_user.id, **form.data)
        db.session.add(comment)
        db.session.commit()

        # fetch all comments posted after `lastmodified`
        if lastmodified:
            comments = Comment.query. \
                filter_by(article_id=comment.article_id). \
                filter(or_(Comment.date_created > cast(lastmodified, DateTime),
                           Comment.last_modified > cast(lastmodified, DateTime))) \
                .order_by(Comment.id).all()
        else:
            # just return this comment when no timestamp is given
            comments = [comment]
        result, error = comments_nested_serializer.dump(comments)
        return {'success': 1, 'status': 200, 'comments': result}
    else:
        flash(form.errors, 'form-error')
        return {'success': 0, 'status': 400}


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
        return redirect(url_for('frontend.index'))

    form = LoginForm(request.form, prefix='l')
    if form.validate_on_submit():
        # username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User.query.filter(User.email_insensitive == email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return {'status': 400, 'success': 0, 'form-error': 1}
        else:
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return {'status': 200, 'success': 1, 'user': user_serializer.dump(user)[0]}

    flash(form.errors, 'danger')
    return {'status': 400, 'success': 0, 'form-error': 1}


@frontend_bp.route('/register/', methods=['POST'])
@xhr_required
def register():

    if g.user and current_user.is_authenticated():
        flash('You are currently logged in as ' + current_user.username + '. If this isn\'t you please logout.', 'warning')
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
        flash('You have successfully registered. You are currently logged in as <strong>' + user.username +'</strong>.', 'success')
        return {'status': 200, 'success': 1}
    else:
        flash(form.errors, 'danger')
        return {'status': 400, 'success': 0, 'form-error': 1}


@frontend_bp.route('/logout/', methods=['GET', 'POST'])
@xhr_or_redirect('frontend.index')
def logout():
    if not current_user.is_authenticated():
        flash('You must be logged in to logout...', 'warning')
        return {'status': 401, 'success': 0}
    logout_user()
    flash('You have successfully logged out.', 'success')
    return {'status': 200, 'success': 1}


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
@xhr_or_redirect('frontend.index')
def unauthorized():
    flash('You are not logged in.', 'danger')
    return {'status': 401, 'success': 0}