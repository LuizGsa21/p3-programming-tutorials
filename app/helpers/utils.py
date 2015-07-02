import pprint
import re
from functools import wraps
from unidecode import unidecode
from flask import request, jsonify, render_template, redirect, json, get_flashed_messages, current_app, url_for, abort
from app.extensions import format_datetime as b_datetime, login_manager


def template_or_json(template=None):
    """"Return a dict from your view and this will either
        pass it to a template or render json.
        Example: @template_or_json('template.html')"""
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if request.is_xhr or not template:
                ctx['flashed_messages'] = format_flashed_messages()
                return jsonify(ctx)
            else:
                return render_template(template, **ctx)
        return decorated_fn
    return decorated


def xhr_or_redirect(route_path):
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if not request.is_xhr:
                return redirect(url_for(route_path))
            pprint.pprint(ctx)

            ctx['flashed_messages'] = format_flashed_messages()
            return jsonify(ctx), ctx['status']
        return decorated_fn
    return decorated


def xhr_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not request.is_xhr:
            abort(404)
        ctx = f(*args, **kwargs)
        ctx['flashed_messages'] = format_flashed_messages()
        return jsonify(ctx), ctx['status']
    return decorator


def format_flashed_messages():
    return [{'category': c, 'message': m} for c, m in get_flashed_messages(with_categories=True)]

def format_datetime(value, format='default'):
    if format == 'default':
        format = 'MMMM d, yyyy'
    elif format == 'full':
        format = 'EEEE, d. MMMM y HH:mm'
    elif format == 'medium':
        format = "EE dd.MM.y HH:mm"
    elif format == 'standard':
        format = 'HH:mm MMMM d, yyyy'
    return b_datetime(value, format)



# taken from: http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))