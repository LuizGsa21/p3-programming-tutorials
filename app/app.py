import os
import pprint

from flask import Flask, render_template, g, flash
from flask_login import current_user, AnonymousUserMixin
from .utils import xhr_or_template

from extensions import db, csrf, login_manager
from config import DevelopmentConfig
from views import api_bp, frontend_bp, user_bp, oauth_bp
from models import Category


# TODO: fix avatar upload, sometimes it overwrites original image
# TODO: fix username registration
# TODO: fix popover. change `This` to field name

DEFAULT_BLUEPRINTS = (api_bp, frontend_bp, user_bp, oauth_bp)


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

    return app


def configure_hook(app):
    @app.before_request
    def before_request():
        g.user = current_user

    @app.context_processor
    def jinja_globals():
        return dict(categories=Category.query.order_by(Category.name).all(), isLoggedIn=current_user.is_authenticated())


def configure_extensions(app):
    # flask SQLAlchemy
    db.init_app(app)
    db.create_all(app=app)

    # CSRF Protection
    csrf.init_app(app)

    @csrf.error_handler
    @xhr_or_template('errors/forbidden-page.html')
    def csrf_error(message):
        flash(message, 'danger')
        return {'status': 400}


    # mail.init_app(app)

    # Login Manger
    login_manager.init_app(app)
    login_manager.login_view = 'frontend.login'

    # Setup login manager anonymous class.
    class DefaultAnonymousUserMixin(AnonymousUserMixin):
        id = None
        firstName = None
        lastName = None
        username = 'Guest'
        email = None
        dateJoined = None
        avatar = 'avatar.jpg'
        # TODO: find an avatar for guest users

    login_manager.anonymous_user = DefaultAnonymousUserMixin


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

    import schemas
    import forms

    @app.template_filter('custom_json')
    def custom_json(obj, serializer, **kwargs):
        if isinstance(serializer, basestring):
            serializer = getattr(schemas, serializer + '_serializer')
            if serializer is None:
                raise ValueError('Invalid serializer')
        return serializer.dumps(obj, **kwargs).data

    @app.template_filter('os_environ')
    def os_environ(key):
        return os.environ.get(key, None)

    @app.template_filter('chunks')
    def chunks(l, n):
        n = max(1, n)
        return [l[i:i + n] for i in range(0, len(l), n)]

    @app.template_filter('capitalize')
    def to_camelcase(word):
        # http://stackoverflow.com/questions/4303492/how-can-i-simplify-this-conversion-from-underscore-to-camelcase-in-python
        def camelcase():
            t = type(word)
            yield t.lower
            while True:
                yield t.capitalize
        c = camelcase()
        return "".join(c.next()(x) if x else '_' for x in word.split("_"))

    def get_form(name, **kwargs):
        form = getattr(forms, name + 'Form')
        if form is None:
            raise ValueError('Invalid form name.')
        return form(**kwargs)

    app.jinja_env.globals['get_form'] = get_form
    # app.jinja_env.trim_blocks = True
    # app.jinja_env.lstrip_blocks = True