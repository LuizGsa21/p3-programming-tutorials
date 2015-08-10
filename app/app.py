from flask import Flask, render_template, g, flash, url_for, redirect, request
from flask_login import current_user, AnonymousUserMixin
from .schemas import frontend_index_view_serializer
from .utils import xhr_or_template

from extensions import db, csrf, login_manager
from config import DevelopmentConfig
from views import api_bp, frontend_bp, user_bp, oauth_bp
from models import Category


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
    """ Configure app hooks. """
    @app.before_request
    def before_request():
        g.user = current_user
        # When a user registers using oauth they will have a temporary username.
        # If the user skips the registration process by closing the window or leaving the page,
        # we have to redirect them to the `oauth.register_username` endpoint.
        #
        # NOTE: when applying the redirect, we need to ignore `oauth.register_username` and `static` endpoints
        #  to prevent an infinite loop and to allow css/js files to still be requested
        if request.endpoint is None:
            # This check covers requests like "GET /favicon.ico HTTP/1.1"
            return  # do nothing
        if '@' in current_user.username and request.endpoint not in ('oauth.register_username', 'static', 'frontend.logout'):
            return redirect(url_for('oauth.register_username'))


def configure_extensions(app):
    """ Configure app extension. """
    # flask SQLAlchemy
    db.init_app(app)
    db.create_all(app=app)

    # CSRF Protection
    csrf.init_app(app)

    @csrf.error_handler
    @xhr_or_template('errors/forbidden-page.html')
    def csrf_error(message):
        flash(message, 'danger')
        return {'status': 403}


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
        avatar = 'avatar.jpg' # TODO: find a better avatar img for guest users

        @staticmethod
        def is_admin():
            return False

    login_manager.anonymous_user = DefaultAnonymousUserMixin


def configure_blueprints(app, blueprints):
    """ Registers blueprints to the applications """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_error_handlers(app):
    """ Set error handlers to the application.
        Note: error handlers from extensions are set in `configure_extensions` method. """

    @app.errorhandler(404)
    def page_not_found(error):
        # use index page schema
        result = frontend_index_view_serializer.dump({
            'user': current_user,
            'navbar': {
                'categories': Category.query.order_by(Category.name).all()
            }
        }).data
        return render_template('errors/page-not-found.html', result=result), 404



def configure_jinja_filters(app):
    """ Set global jinja filters and methods """

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

    # Import forms so we has dynamically access any wtform
    import forms

    def get_form(name, **kwargs):
        """ Returns a wtform using the given `name`
            example:
                `get_form('DeleteCategory')`  returns a DeleteCategoryForm instance
        """

        form = getattr(forms, name + 'Form')
        if form is None:
            raise ValueError('Invalid form name.')
        return form(**kwargs)

    # add `get_form` to jinja's global context
    app.jinja_env.globals['get_form'] = get_form