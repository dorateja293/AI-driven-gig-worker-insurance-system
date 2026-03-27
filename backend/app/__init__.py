from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import config
import os

db = SQLAlchemy()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes import auth, policy, claims, wallet, events, fraud, ml_routes, demo
    app.register_blueprint(auth.bp)
    app.register_blueprint(policy.bp)
    app.register_blueprint(claims.bp)
    app.register_blueprint(wallet.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(fraud.bp)
    app.register_blueprint(ml_routes.bp)
    app.register_blueprint(demo.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
