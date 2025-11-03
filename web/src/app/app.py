import os

from flask import Flask, g, redirect, render_template, request, session

from app.admin.admin import admin_router
from app.anketa.anketa import anketa_router
from app.basic.basic import basic_router
from app.login.login import login_router
from app.auth import auth_required

app = Flask(__name__)
# ! ! ! ! app.config['UPLOAD_FOLDER'] = os.getenv("PATH_TO_USER_UPLOADS", os.path.join(os.getcwd(), "uploads") )

app.secret_key = os.getenv("FLASK_SECRET_KEY", "1111111111")


@admin_router.before_request
@auth_required(require_admin=True)
def _protect_admin():
    pass

@anketa_router.before_request
@auth_required()
def _protect_anketa():
    pass

# app.secret_key = os.urandom(24)

# routers
app.register_blueprint(login_router, url_prefix="/")
app.register_blueprint(basic_router, url_prefix="/basic")
app.register_blueprint(anketa_router, url_prefix="/anketa")
app.register_blueprint(admin_router, url_prefix="/admin")


# # TODO: Сделать нормальную авторизацию через декоратор
# @app.before_request
# def load_user_data():
#     g.is_admin = session.get("adm")
#     protected_paths = ["/admin", "/admin/", "/admin/settings", "/admin/choice", "/anketa", "/anketa/", "/subject/", "/basic"]
#     if any(request.path.startswith(path) for path in protected_paths):  # Критичные маршруты
#         if "user" not in session:
#             return redirect("/")


# Error handling
@app.errorhandler(404)
def not_found(e):
    return render_template("not_found.html", title="Не найдено", body_bg="bg-light"), 404

if __name__ == "__main__":
    #startup()
    app.run(debug=True, port=2222)
