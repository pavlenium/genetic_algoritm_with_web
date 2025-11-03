from functools import wraps
from flask import session, redirect, url_for

def auth_required(_func=None, *, require_admin: bool = False):
    """
    Пример:
      @auth_required
      def view(): ...

      @auth_required(require_admin=True)
      def admin_view(): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = session.get("user")
            if not user:
                return redirect(url_for("core.login"))

            if require_admin and not session.get("adm"):
                return redirect(url_for("basic.basic"))
            return view_func(*args, **kwargs)

        return wrapped
    return decorator if _func is None else decorator(_func)
