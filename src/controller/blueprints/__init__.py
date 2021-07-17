""".. module:: blueprints """
from json import dumps
from functools import wraps

from flask import request, abort, current_app, render_template, g


def valid_roles(roles=None):
    """Handles authentication and authorization of the caller

    This is a decorator for endpoints to stop unallowed access to Resources.
    More (user-)specific authorization checks will be performed in the back-end such as the
    ``application`` or ``search`` package. 

    :param roles: all roles, which are allowed to access the decorated endpoint
    :type roles: list
    """

    def auth_required(func):
        @wraps(func)
        def check_auth(*args, **kwargs):
            if g.munge:
                user = g.username
                current_app.config['APPLICATION'].ensure_existance(user)
            else:
                user = authenticate_via_cookies()
                g.username = user

            user_role = current_app.config['APPLICATION'].get_user_type(user)
            if roles is not None and user_role not in roles:
                abort(401)
            return func(*args, **kwargs)

        return check_auth

    return auth_required

def authenticate_via_cookies() -> str:
    req = {
        'user': request.cookies.get('username'),
        'token': request.cookies.get('token'),
    }

    if current_app.config['APPLICATION'].verify_user_via_token(**req):
        return req['user']
    else:
        abort(401)

def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)

        return decorated_function

    return decorator
