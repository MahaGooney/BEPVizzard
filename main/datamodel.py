# ./main/datamodel.py

import sqlite3
from flask import g, current_app
import click
from colorama import Fore, Back, Style


from auth.datamodel import init_auth_db

# sqlalchemy versuch     from extensions import db

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

class BEP:
    """"""
    # sqlalchemy versuch     
    """
    __tablename__ = 'bep'
    id = db.Column(db.Integer, primary_key=True)
    fixkosten = db.Column(db.Float, nullable=False)
    variable_kosten = db.Column(db.Float, nullable=False)
    menge = db.Column(db.Float, nullable=False)
    preis = db.Column(db.Float, nullable=False)"""


    def __init__(self, id=None, fixkosten=None, variable_kosten=None, menge=None, preis=None):
        self.id = id
        self.fixkosten = fixkosten
        self.variable_kosten = variable_kosten
        self.menge = menge
        self.preis = preis

    @staticmethod
    def get_by_id(id:int)-> 'BEP':
        db = get_db()
        sql = """
            select id, fixkosten, variable_kosten, menge, preis from BEP
            where id = ?;
        """
        item = db.execute(sql, (id, )).fetchone()
        if item is None:
            return None
        return BEP(item['id'], item['fixkosten'], item['variable_kosten'], item['menge'], item['preis'])
        # sqlalchemy versuch   return BEP.query.get(id)

    @staticmethod
    def get_all():
        db = get_db()
        sql = """
            select id, fixkosten, variable_kosten, menge, preis from BEP;
        """
        return [
            BEP(item['id'], item['fixkosten'], item['variable_kosten'], item['menge'], item['preis'])
            for item in db.execute(sql,).fetchall()
        ]
        # sqlalchemy versuch   return BEP.query.all()

    @staticmethod
    def from_dict(value)->'BEP':
        """
        Funktion zum konvertieren eines Dictionarys in ein Termin Objekt
        """
        return BEP(
            value.get('id'),
            value.get('fixkosten'),
            value.get('variable_kosten'),
            value.get('menge'),
            value.get('preis')
            )

    def delete(self, cursor=None, commit=False):
        if not cursor:
            db = get_db()
            cursor = db.cursor()
        sql = "delete from BEP where id = ?;"

        cursor.execute(sql, (self.id,))
        if commit:
            db.commit()
    # sqlalchemy versuch   
    """
    def delete(id):
        bep = BEP.get_by_id(id)
        if bep:
            db.session.delete(bep)
            db.session.commit()
        else:
            raise ValueError(f"BEP with id {id} does not exist.")
    """

    def save(self):
        db = get_db()
        update = """
            update 'BEP'
                set id = :id,
                    fixkosten = :fixkosten, 
                    variable_kosten = :variable_kosten,
                    menge = :menge, 
                    preis = :preis
                where id = :id;
        """
        insert = """
            INSERT INTO 'BEP' 
                (id, fixkosten, variable_kosten, menge, preis)
                values(:id, :fixkosten, :variable_kosten, :menge, :preis);
        """
        affected = db.execute(update, (self.data,)).rowcount
        if affected == 0:
            db.execute(insert, (self.data))
        else:
            db.execute(update, (self.data,))
        db.commit()
        # sqlalchemy versuch   
        """
        if self.id is None:
            db.session.add(self)
        else:
            db.session.merge(self)
        db.session.commit()
        """


    @property
    def data(self:'BEP') -> dict:
        pass

    @data.setter
    def data(self: 'BEP', value: dict):
        pass



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Hilfsfunktionen zu Datenbankinitialisierung per Command Line Parameter
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def init_bep() -> bool:
    KEYWORD = 'init'
    db = get_db()
    if current_app.testing:
        answer = input()
    else:
        click.echo(f"{Back.RED}{Fore.WHITE}!!!                      Achtung                   !!!{Style.RESET_ALL}")
        click.echo("Möchten Sie die Datenbank wirklich neu initialisieren?")
        click.echo("Dies löscht alle vorhandenen Datensätze.")
        click.echo(f"Eingabe {Style.BRIGHT}{Fore.BLUE}{KEYWORD}{Style.RESET_ALL} löscht die Datenbank.")
        click.echo("Alle anderen Eingaben brechen die Funktion ab.")                            
        answer = input()
    if answer == KEYWORD:
        click.echo("Datenbank wird initialisiert...")
        with current_app.open_resource('main/schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        return True
    else:
        click.echo("Initialisierung abgebrochen.")
        return False


@click.command("init-bep")
def init_bep_command():
    answer = init_bep()
    if answer:
        click.echo("BEP-Datenbank initialisiert.")
        init_auth_db()
        click.echo("Authentifizierungsdatenbank initialisiert.")
    else:
        click.echo("BEP-Datenbank nicht initialisiert.")

def init_app(app):
    #app.teardown_appcontext(teardown_bep)
    app.cli.add_command(init_bep_command) 