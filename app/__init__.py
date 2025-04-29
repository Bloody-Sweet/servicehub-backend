from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.models import db
from app.routes.auth import auth_bp
from app.routes.services import services_bp
from app.routes.bookings import bookings_bp
from app.routes.reviews import reviews_bp
from app.routes.providers import providers_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    
    app.register_blueprint(auth_bp, url_prefix='/servicehub')
    app.register_blueprint(services_bp, url_prefix='/servicehub')
    app.register_blueprint(bookings_bp, url_prefix='/servicehub')
    app.register_blueprint(reviews_bp, url_prefix='/servicehub')
    app.register_blueprint(providers_bp, url_prefix='/servicehub')
    
    return app
