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

    # CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    
    CORS(app)
    db.init_app(app)
    
    # @app.after_request
    # def after_request(response):
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    #     response.headers.add('Access-Control-Allow-Credentials', 'true')
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
    #     return response
    
    app.register_blueprint(auth_bp, url_prefix='/servicehub')
    app.register_blueprint(services_bp, url_prefix='/servicehub')
    app.register_blueprint(bookings_bp, url_prefix='/servicehub')
    app.register_blueprint(reviews_bp, url_prefix='/servicehub')
    app.register_blueprint(providers_bp, url_prefix='/servicehub')
    
    return app
