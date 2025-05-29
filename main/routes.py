# ./main/routes.py

from flask import render_template, request
from flask_login import login_required

from . import bp
from .datamodel import BEP
from auth import Permission

@bp.route("/")
def index():
    return render_template("index.html", title = "Home")


@bp.route("/bep_calc")
def bep_calc():
    return render_template("bep.html", title="BEP-Rechner")


@bp.route("/history")
@login_required
def history():
    bep_list = BEP.get_all()
    return render_template("history.html", title="BEP-History")


