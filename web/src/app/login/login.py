import os
from app.postgre.connect import Connect
import requests
from flask import Blueprint, redirect, render_template, request, session, url_for

login_router = Blueprint("core", __name__)


@login_router.route("/")
def index():
    return redirect("/login")


@login_router.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        connect = Connect()
        user = request.form.get("username")
        passw = request.form.get("password")
        if auth(user, passw):
            session["logged_in"] = True
            session["user"] = user
            if user_info(user, 'SchedGen').status_code == 200:
                session["adm"] = True
            session["user"] = user_info(user, 'ScheduleGeneratorAccess')['displayName']
            if not session["user"] in connect.select_teachers():
                connect.insert_teacher(session["user"])
            return redirect(url_for("basic.basic"))
        else:
            return render_template("login.html", title="Вход", error="Неправильные логин или пароль")
    return render_template("login.html", title="Вход")


def user_info(login: str, group: str) -> dict:
    LDAP_API_URL: str = os.getenv("LDAP_API_URL", "http://11.11.1.111:4569")
    login: str = f'{login.split('@')[0]}'
    try:
        response = requests.get(f'{LDAP_API_URL}/info/user',
                                params={'login': login,
                                        'group': group})
        return response.json()
    except Exception as e:
        print('LDAP User error:', e)
    return {}



def auth(login: str, password: str) -> bool:
    LDAP_API_URL: str = os.getenv("LDAP_API_URL", "http://11.11.1.111:4569")
    login: str = f'{login.split('@')[0]}@virtual.local'
    try:
        response = requests.get(f'{LDAP_API_URL}/info/auth',
                                params={'login': login,
                                        'password': password})
        return bool(response)
    except Exception as e:
        print('LDAP Auth error:', e)
    return False

def user_info(login: str, group: str):
    LDAP_API_URL: str = os.getenv("LDAP_API_URL", "http://11.11.1.111:4569")
    login: str = f'{login.split('@')[0]}'
    try:
        response = requests.get(f'{LDAP_API_URL}/info/user',
                                params={'login': login,
                                        'group': group})
        return response
    except Exception as e:
        print('LDAP User error:', e)
    return {}


@login_router.route("/logout")
async def logout():
    session["user"] = None
    session["logged_in"] = False
    session["adm"] = False
    return redirect("/login")
