from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import db, User, Provider

providers_bp = Blueprint('providers', __name__, url_prefix='/api')

@providers_bp.route('/provider-registration', methods=['POST'])
def provider_registration():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name')
    description = data.get('description', '')
    
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 400

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=password_hash, role='provider')
    db.session.add(user)
    db.session.commit()

    provider = Provider(user_id=user.id, company_name=company_name, description=description)
    db.session.add(provider)
    db.session.commit()

    return jsonify({"message": "Provider registered successfully", "provider": provider.to_dict()}), 201

