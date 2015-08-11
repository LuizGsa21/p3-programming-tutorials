from functools import wraps
import pprint
from flask import request, jsonify, render_template, redirect, url_for, abort
from werkzeug.wrappers import Response
from .helpers import format_flashed_messages


def xhr_or_template(template=None):
    """" If a response object is returned, it will simply return the response.
    Otherwise, return a dict from your view and this will either pass it to a template or render json.

    Example dict:
        {'status': 200, 'result': { 'someKey': 'someValue` } }

    `status` - the status value to return
    `result` - a dict containing additional data

    Flashed messages will be fetched and saved to `result`:
        ctx = { 'status': 200, 'result': { 'someKey': 'someValue` } }
        ctx['result']['flashed_messages'] = format_flashed_messages()

    Example Usage:
        @template_or_json('template.html')
        def you_view():
            pass
    """
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
            if not ctx.pop('_delayFlashMessages', None):

                ctx['result']['flashed_messages'] = format_flashed_messages()
            if request.is_xhr or not template:
                return jsonify(ctx),  ctx['status']
            else:
                # pprint.pprint(ctx)
                return render_template(template, result=ctx), ctx['status']

        return decorated_fn

    return decorated


def xhr_or_redirect(route_path):
    """" If the request is NOT a XHR, it redirects to `route_path` using `url_for`.
    Otherwise, return a dict from your view to render a json response.

    Example dict:
        {'status': 200, 'result': { 'someKey': 'someValue` } }

    `status` - the status value to return
    `result` - a dict containing additional data

    Flashed messages will be fetched and saved to `result`:
        ctx = { 'status': 200, 'result': { 'someKey': 'someValue` } }
        ctx['result']['flashed_messages'] = format_flashed_messages()

    Example Usage:
        @xhr_or_redirect('frontend.index')
        def you_view():
            pass
    """
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
    """" If the request is NOT a XHR, an abort 404 error will be thrown.
        Otherwise, return a dict from your view to render a json response.

        Example dict:
            {'status': 200, 'result': { 'someKey': 'someValue` } }

        `status` - the status value to return
        `result` - a dict containing additional data

        Flashed messages will be fetched and saved to `result`:
            ctx = { 'status': 200, 'result': { 'someKey': 'someValue` } }
            ctx['result']['flashed_messages'] = format_flashed_messages()

        Example Usage:
            @xhr_required
            def you_view():
                pass
    """
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