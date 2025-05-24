# ./auth/__init__.py

from flask import Blueprint
from flask_login import LoginManager

bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Bitte melden Sie sich an."
login_manager.login_message_category = "Info"

from .routes import *
from .datamodel import init_app as _init_app
from .datamodel import Permission

def init_app(app):
    login_manager.init_app(app)
    _init_app(app)