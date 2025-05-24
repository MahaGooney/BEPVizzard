# ./main/__init__.py

from flask import Blueprint

bp = Blueprint("main",__name__)

from .routes import *
from .datamodel import init_app as _init_app

def init_app(app):
    _init_app(app)