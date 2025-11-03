from flask import Blueprint, render_template, session

basic_router = Blueprint("basic", __name__)

@basic_router.route("/")
def basic():
    user = session.get("user")
    return render_template("basic.html", title="Основная", user=user)
