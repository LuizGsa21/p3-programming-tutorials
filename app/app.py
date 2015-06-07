from flask import Flask, render_template, g, flash, url_for, redirect

from config import DevelopmentConfig
from extensions import db, csrf, login_manager, oid, current_user, mail, babel
from .admin import admin_bp
from .api import api_bp
from .frontend import frontend_bp
from .user import user_bp
from .oauth import oauth_bp
from .models import Category, init_database
from utils import format_datetime


DEFAULT_BLUEPRINTS = (admin_bp, api_bp, frontend_bp, user_bp, oauth_bp)


def create_app(app_name=None, blueprints=None, config=None):
    """Creates and returns a Flask application"""

    # Load default settings
    if app_name is None:
        app_name = DevelopmentConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS
    if config is None:
        config = DevelopmentConfig

    app = Flask(app_name, template_folder=config.TEMPLATE_FOLDER, static_folder=config.STATIC_FOLDER)

    app.config.from_object(config)
    configure_extensions(app)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_error_handlers(app)
    configure_jinja_filters(app)

    # from .models import init_database
    with app.app_context():
        init_database()

    return app


def configure_hook(app):
    @app.before_request
    def before_request():
        g.user = current_user

    @app.context_processor
    def jinja_globals():
        return dict(categories=Category.query.all())


def configure_extensions(app):
    db.init_app(app)
    db.create_all(app=app)

    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'frontend.index'

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('You are not logged in.', 'danger')
        return redirect(url_for('frontend.index'))

    oid.fs_store_path = 'openid-store'
    oid.init_app(app)

    mail.init_app(app)

    babel.init_app(app)

    # https://pythonhosted.org/Flask-Babel/
    # @babel.localeselector
    # def get_locale():
    ## There is no locale user setting yet
    # user = getattr(g, 'user', None)
    # if user is not None:
    #     return user.locale
    #
    # return request.accept_languages.best_match(['de', 'fr', 'en'])
    #
    # @babel.timezoneselector
    # def get_timezone():
    #     user = getattr(g, 'user', None)
    #     if user is not None:
    #         return user.timezone


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template('errors/forbidden-page.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/page-not-found.html'), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template('errors/server-error.html'), 500


def configure_jinja_filters(app):
    @app.template_filter('datetime')
    def datetime(*args, **kwargs):
        return format_datetime(*args, **kwargs)