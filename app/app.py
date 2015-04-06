from flask import Flask, request, render_template
from config import DevelopmentConfig
from extensions import db, csrf, login_manager, oid

from admin import admin
from api import api
from frontend import frontend
from user import user

DEFAULT_BLUEPRINTS = (admin, api, frontend, user)


def create_app(app_name=None, blueprints=None, config=None):
    """Creates and returns a Flask application"""

    # Load default settings
    if app_name is None:
        app_name = DevelopmentConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS
    if config is None:
        config = DevelopmentConfig

    app = Flask(app_name, template_folder=config.PROJECT_TEMPLATES)
    app.config.from_object(config)
    configure_hook(app)
    configure_extensions(app)
    configure_blueprints(app, blueprints)
    configure_error_handlers(app)

    return app


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_extensions(app):

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    oid.init_app(app)


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