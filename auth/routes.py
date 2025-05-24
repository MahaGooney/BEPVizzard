# ./auth/routes.py

from http import HTTPStatus
from functools import wraps
from secrets import token_urlsafe
import json
from flask import render_template, redirect, abort, request, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required

from . import bp
from .datamodel import User, Role, Permission

# Definition des Decorators für das Prüfen der Berechtigungen
def permission_required(permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.can(permissions):
                return f(*args, **kwargs)
            else: 
                flash(f"Nutzer {current_user.name} hat die Rechte {permissions} nicht.", "danger")
                abort(HTTPStatus.FORBIDDEN)
        return wrapped
    return wrapper


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        option = request.form["submit"]
        if option == "cancel":
            return redirect(url_for("main.index"))
        user = User.get_by_name(username)
        if user and user.validate_password(password):
            login_user(user)
            flash(f"{username} wurde erfolgreich angemeldet.", "success")
            return redirect(url_for("main.index"))
        else:
            flash(f"Username oder Passwort ungültig", "danger")
            return redirect(url_for("auth.login"))
    return render_template("login.html", title="Login")


@bp.route("/logout")
def logout():
    name = current_user.name    
    logout_user()
    flash(f"{name} wurde abgemeldet", "success")
    return redirect(url_for("main.index"))

