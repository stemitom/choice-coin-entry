from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ, path
from dotenv import load_dotenv

basedir = path.dirname(path.abspath(__file__))
load_dotenv(path.join(basedir, ".env"), verbose=True)

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config["FLASK_DEBUG"] = environ.get("FLASK_DEBUG")
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        from . import models, routes

        return app
