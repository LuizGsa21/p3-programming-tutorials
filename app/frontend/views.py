import pprint
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import array
from app.extensions import db, login_manager, current_user, login_user, \
    logout_user, login_required, oauth, Message, mail
from app.helpers.utils import xhr_required
from forms import LoginForm, RegisterForm, CommentForm
from sqlalchemy.dialects.postgresql import ARRAY
from app.models import User, Article, Category, Comment
from sqlalchemy import type_coerce, Integer, or_
from sqlalchemy.sql.expression import literal
from app.api.schemas import comments_nested_serializer
from sqlalchemy import DateTime, cast

frontend_bp = Blueprint('frontend', __name__)

login_manager.login_view = 'frontend.login'

@frontend_bp.route('/')
def index():
    forms = {'register': RegisterForm(prefix='r'), 'login': LoginForm(prefix='l')}

    return render_template('frontend/index.html', active_page='index', forms=forms)

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

    cte = db.session.query(Comment,
                           array([Comment.id]).label('path'),
                           literal(0, type_=Integer).label('depth')
                           ) \
        .filter_by(parent_id=None)\
        .cte(name='cte', recursive=True)

    c1_alias = aliased(cte, name='c1')
    c2_alias = aliased(Comment, name='c2')

    cte = cte.union_all(
        db.session.query(c2_alias,
                         c1_alias.c.path + array([c2_alias.id]).label('path'),
                         c1_alias.c.depth + literal(1, type_=Integer).label('depth'))
            .join(c1_alias, c2_alias.parent_id==c1_alias.c.id))

    result = db.session.query(Comment,
                              type_coerce(cte.c.path, ARRAY(Integer, as_tuple=True)),
                              cte.c.depth
                              ).\
                              select_entity_from(cte).order_by('path').all()
    forms = {
        'commentForm': CommentForm(article_id=article.id),
        'register': RegisterForm(prefix='r'),
        'login': LoginForm(prefix='l')
    }

    parents = [] # comments referring to the article.
    children = [] # comments referring to other comments
    for comment, path , depth in result:
        if depth == 0: # if its a parent
            children = []
            parents.append((comment, depth, children))
        else:
            children.append((comment, depth, None))

    return render_template('frontend/tutorial.html', comments=parents, article=article, forms=forms)


@frontend_bp.route('/add/comment', methods=['POST'])
@login_required
@xhr_required
def add_comment():
    form = CommentForm(request.form)
    lastmodified = request.form.get('lastmodified')

    if form.validate_on_submit():
        comment = Comment(user_id=current_user.id, **form.data)
        db.session.add(comment)
        db.session.commit()

        # get the new comments according to the given `lastmodified` value
        if lastmodified:
            comments = Comment.query.\
                filter_by(article_id=comment.article_id).\
                filter(or_(Comment.date_created > cast(lastmodified, DateTime),
                           Comment.last_modified > cast(lastmodified, DateTime)))\
                .order_by(Comment.id).all()
        else:
            comments = [comment]
        result, error = comments_nested_serializer.dump(comments)
        return {'success':1, 'status': 200, 'comments': result}
    else:
        flash(form.errors, 'form-error')
        return {'success':0, 'status': 400}

@frontend_bp.route('/mail/')
def send_mail():
    msg = Message('Hello its luiz :)',
                  body='this is an email. lol',
                  recipients=['larantessa@icloud.com'])
    mail.send(msg)
    return redirect(url_for('frontend.index'))


@frontend_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if g.user and current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('frontend.index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        # username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User.query.filter(User.email_insensitive == email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('frontend.index'))
        else:
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('frontend.index'))
    flash(form.errors, 'danger')
    return redirect(url_for('frontend.index'))


@frontend_bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            pwdhash=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered. Please login.', 'success')
        return redirect(url_for('frontend.index'))
    flash(form.errors, 'form-errors')
    return redirect(url_for('frontend.index'))


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


@frontend_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('frontend.index'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You are not logged in.', 'danger')
    return redirect(url_for('frontend.index'))