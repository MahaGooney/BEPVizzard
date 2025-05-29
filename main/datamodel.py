# ./main/datamodel.py

from flask import g, current_app
import click
from colorama import Fore, Back, Style


from auth.datamodel import init_auth_db

class BEP:
    def __init__(self, id=None, fixkosten=None, variable_kosten=None, menge=None, preis=None):
        self.id = id
        self.fixkosten = fixkosten
        self.variable_kosten = variable_kosten
        self.menge = menge
        self.preis = preis

    @staticmethod
    def get_by_id(id):
        pass

    @staticmethod
    def get_all():
        pass

    def delete(id):
        pass

    def save(self):
        pass

    def update(self):
        pass
        


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