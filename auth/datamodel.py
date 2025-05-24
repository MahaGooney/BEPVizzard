# ./auth/datamodel.py

from enum import IntFlag, auto
from flask import Flask, g, current_app
from flask_login import UserMixin, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager

# Hier wird die SQLite DB mit der App verbunden.
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bep.db"
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

class Permission(IntFlag):
    NONE            = 0 
    ADMIN           = auto()
    BEP             = auto()
    BEP_history     = auto()


class Role:
    __tablename__ = 'role'
    id =db.Column(db.string(20), primary_key = True)
    permissions = db.Column(db.integer, nullable = False)
    standard = db.Column(db.integer)


    @staticmethod
    def init_roles(): 
        roles = {
            'Anonymous':    Permission.BEP,
            'Admin':        Permission.Admin | Permission.BEP | Permission.BEP_history,
            'User':         Permission.BEP | Permission.BEP_history
        } # Dictionarys welche Rolle welche Rechte bekommt
        standard_role = 'Anonymous' # Standardrolle wird auf Anonymous festgelegt
        for role, permissions in roles.items(): # Anlegen aller Rollen im Dictionary
            r = Role.get(role)
            if r is None:  # Prüfung ob die Rolle schon existiert
                r=Role(name=role)
            r.name = role
            r.permissions = permissions
            r.standard = (role == standard_role)
            r.save()

    def __init__(self, name=None, permissions = Permission.NONE, standard = False):
        if name is None:
            raise ValueError("Role missing parameter 'name'")
        self.id = id
        self.name = name
        self. permissions = permissions
        self.standard = bool(standard)

    @staticmethod
    def get(name):
        pass

    def save(self, commit=True):
        pass



    
class User:
    __tablename__ = 'user'
    id =db.Column(db.integer, primary_key = True, autoincrement = True)
    name = db.Column(db.string(40), nullable = False)
    email = db.Column(db.string(40), nullable = False)
    password = db.Column(db.string(40), nullable = False)
    role_id = db.Column(db.string(20), ForeignKey('role.id'), nullable = False)

    @staticmethod
    def get(id):
        pass

    def save(self):
        pass


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.name = "Anonymous"
        self.email = "anonymous@email.com"
        self.role = Role.get("Anonymous")

    def can(self, permission):
        return False
    
login_manager.anonymous_user = AnonymousUser

def init_auth_db():
    pass