from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        # Import parts of our application
        from app.urls import api_blueprint

        app.register_blueprint(api_blueprint, url_prefix="/api")

        # Import our models for SQLAlchemy
        from app import models

    return app
