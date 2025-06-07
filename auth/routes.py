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

@bp.route("/userlist")
@permission_required(Permission.ADMIN)
def userlist():
    users = User.get_all()
    return render_template("userlist.html", title="Userlist", users=users)

@bp.route("/add_user", methods=["GET", "POST"])
@permission_required(Permission.ADMIN)
def add_user():
    roles = Role.get_all()
    if request.method == "POST":
        option = request.form["submit"]
        if option == "cancel":
            return redirect(url_for("auth.userlist"))
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        password = token_urlsafe(16)  

        existing = User.get_by_name(name)
        if existing:
            flash(f"Benutzer {name} existiert bereits.", "danger")
            return redirect(url_for("auth.add_user"))
        existing = User.get_by_email(email)
        if existing:
            flash(f"Benutzer mit Email {email} existiert bereits.", "danger")
            return redirect(url_for("auth.add_user"))
        if role not in [r.name for r in roles]:
            flash(f"Rolle {role} existiert nicht.", "danger")
            return redirect(url_for("auth.add_user"))
        new = User(name=name, email=email, password=password, role=role)
        new.save()
        flash(f"Benutzer {name} mit Rolle {role} und Passwort {password} wurde angelegt.", "success")
        return redirect(url_for("auth.userlist"))
    return render_template("add_user.html", title="Add User", roles=roles)

@bp.route("/user/<int:id>/edit", methods=["GET", "POST"])
@permission_required(Permission.ADMIN)
def edit_user(id):
    user = User.get_by_id(id)
    if user is None:
        flash(f"Benutzer mit ID {id} existiert nicht.", "danger")
        return redirect(url_for("auth.userlist"))
    if request.method == "POST":
        option = request.form["submit"]
        if option == "cancel":
            return redirect(url_for("auth.userlist"))
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        try:
            assert name, "Name darf nicht leer sein."
            if name != user.name:
                assert user.get_by_name(name) is None, f"Benutzer {name} existiert bereits."
                user.name = name
            assert email, "Email darf nicht leer sein."
            if email != user.email:
                assert user.get_by_email(email) is None, f"Benutzer mit Email {email} existiert bereits."
                user.email = email
            if role != user.role.name:
                if user.role.name != "Anonymous":
                    assert user.role.usercount > 1, f"Der User {user.name} ist der letzte Nutzer mit der Rolle {user.role.name} und kann nicht gelöscht werden."
                user.role = Role.get(role)
            user.save()
            flash(f"Benutzer {user.name} wurde aktualisiert.", "success")
            return redirect(url_for("auth.userlist"))
        except AssertionError as e:
            flash(str(e), "danger")
            return redirect(url_for("auth.edit_user", id=id))
    roles = Role.get_all()
    return render_template("user.html", title="Edit User", user=user, roles=roles)

@bp.route("/user/<int:id>/delete", methods=["POST"])
@permission_required(Permission.ADMIN)
def delete_user(id):
    user = User.get_by_id(id)
    if user.id == current_user.id:
        flash("Der aktuelle Nutzer kann nicht gelöscht werden.", "danger")
    elif user.role.usercount == 1:
        flash(f"Der User {user.name} ist der letzte Nutzer mit der Rolle {user.role.name} und kann nicht gelöscht werden.", "danger")
    else:
        name = user.name
        user.delete()
        flash(f"Benutzer {name} wurde gelöscht.", "success")
    return redirect(url_for("auth.userlist"))

@bp.route("/user/<int:id>/reset_password")
@permission_required(Permission.ADMIN)
def reset_password(id):
    user= User.get_by_id(id)
    if user.id == current_user.id:
        return redirect(url_for("auth.change_password"))
    password = token_urlsafe(16)
    user.password = password
    user.save()
    flash(f"Passwort für {user.name} wurde zurückgesetzt. Neues Passwort: {password}", "success")
    return redirect(url_for("auth.userlist"))

@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    min_length = 8
    user = current_user
    if request.method == "POST":
        option = request.form["submit"]
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        if option == "cancel":
            return redirect(url_for("main.index"))
        if not user.validate_password(old_password):
            flash("Altes Passwort ist falsch.", "danger")
            return redirect(url_for("auth.change_password"))
        if new_password != confirm_password:
            flash("Neues Passwort und Bestätigung stimmen nicht überein.", "danger")
            return redirect(url_for("auth.change_password"))
        if len(new_password) < min_length:
            flash(f"Neues Passwort muss mindestens {min_length} Zeichen lang sein.", "danger")
            return redirect(url_for("auth.change_password"))
        user.password = new_password
        if user.validate_password(new_password):
            user.save()
            flash("Passwort wurde erfolgreich geändert.", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Passwortänderung fehlgeschlagen. Bitte versuchen Sie es erneut.", "danger")
            return redirect(url_for("auth.change_password"))
    return render_template("change_password.html", title="Change Password", user=user, min_length=min_length)

@bp.route("/profile")
@login_required
def profile():
    user = User.get(current_user.id)
    return render_template("profile.html", user = user, title = f"{user.name} - Profil")

@bp.route("/change_username")
@login_required
def change_username():
    pass

@bp.route("/change_email")
@login_required
def change_email():
    pass

@bp.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html", title="Register")
