# ./bep.py

import os 
from flask import Flask, request

def init_config(app, test_config=None):
    pass

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
    create_instance_path(app)
    init_blueprints(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)