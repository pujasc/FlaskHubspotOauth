import logging
import os

from dotenv import load_dotenv
from flask import Flask, request, redirect, app
from flask_session import Session

from Hubspot_login import happ

sess = Session()

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = os.urandom(24).__str__()
    app.debug = True
    sess.init_app(app)

    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    with app.app_context():
        app.register_blueprint(happ)
        return app

if __name__ == "__main__":
    app.run()