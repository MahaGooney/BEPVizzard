# ./main/datamodel.py

from flask import g, current_app
import click
from colorama import Fore, Back, Style


from auth.datamodel import init_auth_db

from extensions import db

class BEP:
    __tablename__ = 'bep'
    id = db.Column(db.Integer, primary_key=True)
    fixkosten = db.Column(db.Float, nullable=False)
    variable_kosten = db.Column(db.Float, nullable=False)
    menge = db.Column(db.Float, nullable=False)
    preis = db.Column(db.Float, nullable=False)


    def __init__(self, id=None, fixkosten=None, variable_kosten=None, menge=None, preis=None):
        self.id = id
        self.fixkosten = fixkosten
        self.variable_kosten = variable_kosten
        self.menge = menge
        self.preis = preis

    @staticmethod
    def get_by_id(id):
        return BEP.query.get(id)

    @staticmethod
    def get_all():
        return BEP.query.all()

    def delete(id):
        bep = BEP.get_by_id(id)
        if bep:
            db.session.delete(bep)
            db.session.commit()
        else:
            raise ValueError(f"BEP with id {id} does not exist.")

    def save(self):
        if self.id is None:
            db.session.add(self)
        else:
            db.session.merge(self)
        db.session.commit()
        


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Hilfsfunktionen zu Datenbankinitialisierung per Command Line Parameter
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def init_bep() -> bool:
    KEYWORD = 'init'

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
        pass


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