from functools import wraps

from flask import redirect, session, url_for


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in", False):
            return redirect(url_for("core.login"), code=303)
        return f(*args, **kwargs)

    return decorated_function
