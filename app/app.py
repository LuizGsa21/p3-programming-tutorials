import os

from flask import Flask, render_template, g

from config import DevelopmentConfig
from extensions import db, csrf, login_manager, current_user, babel
from .admin import admin_bp
from .api import api_bp
from .frontend import frontend_bp
from .user import user_bp
from .oauth import oauth_bp
from .models import Category, init_database
from .helpers.utils import format_datetime, slugify
from .helpers.momentjs import momentjs


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

    # mail.init_app(app)
    babel.init_app(app)


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

    @app.template_filter('slug')
    def slug(url, delim=u'-'):
        return slugify(url, delim=u'-')

    @app.template_filter('custom_json')
    def custom_json(obj, serializer):
        import json
        result, error = serializer.dump(obj)
        return json.dumps(result)

    @app.template_filter('os_environ')
    def os_environ(key):
        return os.environ.get(key, None)

    @app.template_filter('chunks')
    def chunks(l, n):
        n = max(1, n)
        return [l[i:i + n] for i in range(0, len(l), n)]

    # TODO: replace this with the current datetime filter
    @app.template_filter('fromnow')
    def fromnow(timestamp):

        return momentjs(timestamp).fromNow()