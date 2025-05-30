# ./auth/datamodel.py

from enum import IntFlag, auto
from flask import Flask, g, current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

class Permission(IntFlag):
    NONE            = 0 
    ADMIN           = auto()
    BEP             = auto()
    BEP_history     = auto()


class Role(db.Model):
    __tablename__ = 'role'
    id =db.Column(db.String(20), primary_key = True)
    permissions = db.Column(db.Integer, nullable = False)
    standard = db.Column(db.Integer)


    @staticmethod
    def init_roles(): 
        roles = {
            'Anonymous':    Permission.BEP,
            'Admin':        Permission.ADMIN | Permission.BEP | Permission.BEP_history,
            'User':         Permission.BEP | Permission.BEP_history
        } # Dictionarys welche Rolle welche Rechte bekommt
        standard_role = 'Anonymous' # Standardrolle wird auf Anonymous festgelegt
        for role, permissions in roles.items(): # Anlegen aller Rollen im Dictionary
            r = Role.get_by_name(role)
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
        self.permissions = permissions
        self.standard = bool(standard)

    @staticmethod
    def get_by_name(name):
        return Role.query.get(name)

    @staticmethod
    def get_all():
          return Role.query.all()

    def save(self, commit=True):
        if self.id is None:
            self.id = self.name
            db.session.add(self)
        else:
            db.session.merge(self)
        if commit:
            db.session.commit()

    def can(self, permission):
        print(f"Role.can called with {permission = }")
        print(f"Role {self} has permissions {self.permissions}")
        ret = bool(self.permissions & permission)
        print(f"Role.can ended with {ret = }")
        return ret    
    
    @property
    def data(self):
        return {
            "name": self.name,
            "permissions": int(self.permissions),
            "standard": self.standard
        }

    @data.setter
    def data(self, value):
        self.name = value["name"]
        self.permissions = value["permissions"]
        self.standard = value["standard"]

    @property
    def usercount(self):
        return Role.query.filter_by(role_id=self.id).count()

    @usercount.setter
    def usercount(self, value):
        raise ValueError("Role.usercount is read-only property!")



    
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id =db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(40), nullable = False)
    email = db.Column(db.String(40), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    role_id = db.Column(db.String(20), db.ForeignKey('role.id'), nullable = False)

    def __init__(self, id=None, name=None, email=None, password=None, password_hash=None, role=None):
        assert name is not None, "User missing parameter 'name'"
        assert email is not None, "User missing parameter 'email'"
        assert password is not None or password_hash is not None, "User missing parameter 'password' or 'password_hash'"
        assert role is not None, "User missing parameter 'role'"
        self.id = id
        self.name = name
        self.email = email  
        if password is not None:
            self.password = password
        else:
            self.password_hash = password_hash
        self.role = Role.get_by_name(role)

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    def get_by_name(name):
        return User.query.filter_by(name=name).first()

    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all():
        return User.query.all()

    def save(self):
        if self.id is None:
            db.session.add(self)
        else:
            db.session.merge(self)
        db.session.commit()

    def delete(self):
        if self.role.name != "Anonymous":
            assert self.role.usercount > 1, f"Der User {self.name} ist der letzte Nutzer mit der Rolle {self.role.name} und kann nicht gelöscht werden."
        db.session.delete(self)
        db.session.commit()

    def can(self, permission):
        return self.role.can(permission)
    
    def get_id(self):
        return self.id

    @property
    def password(self):
        raise PermissionError("Password is not readable")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, value):
        return check_password_hash(self.password_hash, value)

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password_hash,
            "role": self.role
        }
    
    @data.setter
    def data(self, value):
        self.id = value["id"]
        self.name = value["name"]
        self.email = value["email"]
        self.password_hash = value["password"]
        self.role = Role.get(value["role"])

    @property
    def is_admin(self):
        return self.role.can(Permission.ADMIN)
    
    @is_admin.setter
    def is_admin(self, value):
        raise PermissionError("is_admin cannot be set directly, use role management instead")
     


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.name = "Anonymous"
        self.email = "anonymous@email.com"
        self.role = Role.get_by_name("Anonymous")

    def can(self, permission):
        return False
    
login_manager.anonymous_user = AnonymousUser

def init_app(app):
    pass

def init_auth_db():
    Role.init_roles()
    for r in Role.get_all():
        if r.name != "Anonymous":
            u = User(None, r.name, f"{r.name}@bep.de", "geheim", None, r.name)
            u.save()