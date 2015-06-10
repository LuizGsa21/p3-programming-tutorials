from functools import wraps
from flask import request, jsonify, render_template, redirect, json, get_flashed_messages, current_app, url_for
from extensions import format_datetime as b_datetime

def template_or_json(template=None):
    """"Return a dict from your view and this will either
        pass it to a template or render json.
        Example: @template_or_json('template.html')"""
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if request.is_xhr or not template:
                ctx['flashed_messages'] = \
                    [{'category':c, 'message': m} for c, m in get_flashed_messages(with_categories=True)]
                return jsonify(ctx)
            else:
                return render_template(template, **ctx)
        return decorated_fn
    return decorated

def redirect_or_json(redirect_url):
    def decorator(f):
        @wraps(f)
        def decorator_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if request.is_xhr:
                ctx['flashed_messages'] = \
                    [{'category':c, 'message': m} for c, m in get_flashed_messages(with_categories=True)]
                return jsonify(ctx), ctx['status']
            else:
                return redirect(url_for(redirect_url))
        return decorator_fn
    return decorator

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config.get('ALLOWED_EXTENSIONS', ('',))