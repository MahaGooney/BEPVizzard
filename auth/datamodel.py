# ./auth/datamodel.py

import sqlite3
from enum import IntFlag, auto
from flask import Flask, g, current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# sqlalchemy versuch     from extensions import db

from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

class Permission(IntFlag):
    NONE            = 0 
    ADMIN           = auto()
    BEP             = auto()
    BEP_history     = auto()


# sqlalchemy versuch     class Role(db.Model):
    # sqlalchemy versuch     __tablename__ = 'role'
    # sqlalchemy versuch     id =db.Column(db.String(20), primary_key = True)
    # sqlalchemy versuch     permissions = db.Column(db.Integer, nullable = False)
    # sqlalchemy versuch     standard = db.Column(db.Integer)

class Role():
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
        db = get_db()
        sql = "select * from 'role' where name = ?;"
        item = db.execute(sql, (name,)).fetchone()
        if item is None:
            return Role.get_default()
        else:
            return Role.from_dict(item)
        # sqlalchemy versuch     return Role.query.get(name)

    @staticmethod
    def get_by_userid(id):
        db = get_db()
        sql = """select r.name, r.permissions, r.standard from user u 
                INNER JOIN role r on u.role_id = r.name
                where u.id = ?;
        """
        item = db.execute(sql, (id,)).fetchone()
        if item is None:
            return Role.get_standard()
        else:
            return Role.from_dict(item)

    @staticmethod
    def get_default():
        db = get_db()
        sql = "select * from 'role' where 'standard'=1"
        item = db.execute(sql).fetchone()
        if item is None:
            return Role("Anonymous", Permission.NONE, True)
        else:
            return Role.from_dict(item)

    @staticmethod
    def get_all():
        db = get_db()
        sql = "select * from 'role';"
        return [
            Role.from_dict(item)
            for item in db.execute(sql).fetchall()
        ]
          # sqlalchemy versuch     return Role.query.all()

    def from_dict(item):
        return Role(item['name'], item['permissions'], item['standard'])
    
    def save(self, commit=True):
        db = get_db()
        print(f"Saving role {self.name}.")
        update = """
            update 'role'
            set 'name' = :name,
                'permissions' = :permissions,
                'standard' = :standard
            where 'name' = :name;
        """
        insert = """
            insert into 'role'
            ('name', 'permissions', 'standard')
            values (:name, :permissions, :standard);
        """
        affected = db.execute(update, self.data).rowcount
        if affected == 0:
            db.execute(insert, self.data)
        else:
            db.execute(update, self.data)
        
        if commit:
            db.commit()

        # sqlalchemy versuch     
        """
        if self.id is None:
            self.id = self.name
            db.session.add(self)
        else:
            db.session.merge(self)
        if commit:
            db.session.commit()
        """


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
        self.name           = value["name"]
        self.permissions    = value["permissions"]
        self.standard       = value["standard"]

    @property
    def usercount(self):
        db = get_db()
        sql = "select count(*) as 'count' from 'user' where role_id = ?;"
        item = db.execute(sql, (self.name,)).fetchone()
        return int(item['count'])
        # sqlalchemy versuch     return Role.query.filter_by(role_id=self.id).count()

    @usercount.setter
    def usercount(self, value):
        raise ValueError("Role.usercount is read-only property!")


# sqlalchemy versuch     
"""
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id =db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(40), nullable = False)
    email = db.Column(db.String(40), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    role_id = db.Column(db.String(20), db.ForeignKey('role.id'), nullable = False)
"""   
class User(UserMixin):

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
    def from_dict(item):
        return User(item['id'], item['name'], item['email'], None, item['password'], item['role_id'])

    @staticmethod
    def get_by_id(id):
        db = get_db()
        sql = "select * from 'user' where id = ?;"
        item = db.execute(sql, (int(id),)).fetchone()
        return None if item is None else User.from_dict(item)
        # sqlalchemy versuch     return User.query.get(id)

    @staticmethod
    def get_by_name(name):
        db=get_db()
        sql = """SELECT * FROM 'user' WHERE "name" = ? OR "email" = ?;"""
        item = db.execute(sql, (name, name)).fetchone()
        return None if item is None else User.from_dict(item)
        # sqlalchemy versuch     return User.query.filter_by(name=name).first()

    @staticmethod
    def get_all():
        db = get_db()
        sql = "select * from 'user';"
        return [
            User.from_dict(item)
            for item in db.execute(sql).fetchall()
        ]
        # sqlalchemy versuch     return User.query.all()

    def save(self):
        db = get_db()
        if self.id is not None:
            sql = """
                UPDATE 'user'
                SET 'name' = :name,
                    'password' = :password,
                    'email'    = :email,
                    'role_id'  = :role_id
                WHERE
                    "id"       = :id
            """
        else:
            sql="""
                INSERT INTO 'user'
                ('name', 'password', 'email', 'role_id')
                VALUES
                (:name, :password, :email, :role_id)
            """
        db.execute(sql, self.data)
        if self.data is None: 
            self.id = db.execute("select last_insert_rowid()").fetchone()[0]
        db.commit()
        # sqlalchemy versuch     
        """if self.id is None:
            db.session.add(self)
        else:
            db.session.merge(self)
        db.session.commit()"""

    def delete(self):
        db = get_db()
        cursor = db.cursor()
        sql = "delete from 'user' where id=?;"
        cursor.execute(sql, (self.id, ))
        db.commit()
        # sqlalchemy versuch     
        """if self.role.name != "Anonymous":
            assert self.role.usercount > 1, f"Der User {self.name} ist der letzte Nutzer mit der Rolle {self.role.name} und kann nicht gelöscht werden."
        db.session.delete(self)
        db.session.commit()"""

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
            "role_id": self.role.name
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