from functools import wraps
import pprint
from flask import request, jsonify, render_template, redirect, url_for, abort
from werkzeug.wrappers import Response
from .helpers import format_flashed_messages


def xhr_or_template(template=None):
    """"Return a dict from your view and this will either
        pass it to a template or render json.
        Example: @template_or_json('template.html')"""

    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            # just return the object if its a response object
            if isinstance(ctx, Response):
                return ctx
            # add a result attribute if not yet set
            if 'result' not in ctx:
                ctx['result'] = {}
            # add flash messages
            ctx['result']['flashed_messages'] = format_flashed_messages()
            if request.is_xhr or not template:
                return jsonify(ctx),  ctx['status']
            else:
                return render_template(template, result=ctx)

        return decorated_fn

    return decorated


def xhr_or_redirect(route_path):
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if not request.is_xhr:
                return redirect(url_for(route_path))
            # add a result key if not yet set
            if 'result' not in ctx:
                ctx['result'] = {}
            # add flash messages
            ctx['result']['flashed_messages'] = format_flashed_messages()
            return jsonify(ctx), ctx['status']
        return decorated_fn
    return decorated


def xhr_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not request.is_xhr:
            abort(404)
        ctx = f(*args, **kwargs)
        # add a result key if not yet set
        if 'result' not in ctx:
            ctx['result'] = {}
        # add flash messages
        ctx['result']['flashed_messages'] = format_flashed_messages()
        return jsonify(ctx), ctx['status']
    return decorator