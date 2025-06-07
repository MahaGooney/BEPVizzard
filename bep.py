# ./bep.py

import os 
from flask import Flask, request
# sqlalchemy versuch     from extensions import db
# sqlalchemy versuch     from config import Config


def init_config(app, test_config= None):
    DB_FILE = os.path.join(app.instance_path, "bep.sqlite")
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE = DB_FILE
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

def create_instance_path(app):
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def init_blueprints(app):
    import main
    app.register_blueprint(main.bp)
    main.init_app(app)

    import auth
    app.register_blueprint(auth.bp)
    auth.init_app(app)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    init_config(app, test_config)

    # sqlalchemy versuch     
    """
    app.config.from_object(Config)
    db.init_app(app)
    """
    create_instance_path(app)
    init_blueprints(app)
    # sqlalchemy versuch     
    """
    with app.app_context():
        db.create_all()
    """
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)