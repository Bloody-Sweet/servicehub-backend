from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import with_polymorphic
from app.models import db, User, Customer, Provider, Admin
import re
auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    print("data",data)
    
    first_name = data.get('first_name') or data.get('firstname')
    last_name = data.get('last_name') or data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'customer') 

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    password_hash = generate_password_hash(password)

    try:
        if role == 'customer':
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=password_hash,
                role=role,
                address=data.get('address'),
                phone_number=data.get('phone_number'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                is_active=data.get('is_active', True)
            )
            phone_number = data.get('phone_number')
            if not re.fullmatch(r'\d{3}-\d{3}-\d{4}', str(phone_number)):
                return jsonify({"error": "Phone number must be in the format 212-555-1234"}), 400
            
            db.session.add(customer)
            db.session.commit()
            return jsonify({"message": "Customer registered successfully", "user": customer.to_dict()}), 201

        elif role == 'provider':
            provider = Provider(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=password_hash,
                role=role,
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                phone_number=data.get('phone_number'),
                company_name=data.get('company_name') or "Default Company",
                description=data.get('description'),
                ratings=data.get('ratings', 0.0)
            )
            phone_number = data.get('phone_number')
            if not re.fullmatch(r'\d{3}-\d{3}-\d{4}', str(phone_number)):
                return jsonify({"error": "Phone number must be in the format 212-555-1234"}), 400
        
            db.session.add(provider)
            db.session.commit()
            return jsonify({"message": "Provider registered successfully", "user": provider.to_dict()}), 201

        elif role == 'admin':
            admin = Admin(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=password_hash,
                role=role
            )
            db.session.add(admin)
            db.session.commit()
            return jsonify({"message": "Admin registered successfully", "user": admin.to_dict()}), 201

        else:
            return jsonify({"error": "Invalid role specified"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user_poly = with_polymorphic(User, '*')
    user = db.session.query(user_poly).filter(User.email == email).first()
    
    if not user:
        return jsonify({
            "message": "User not found"
        })

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "message": "Invalid credentials"
        })

    if user and check_password_hash(user.password_hash, password):
        if user.role == 'customer':
            return jsonify({
                "message": "Customer login successful",
                "role": "customer",
                "user": user.to_dict()
            })
        elif user.role == 'provider':
            return jsonify({
                "message": "Provider login successful",
                "role": "provider",
                "user": user.to_dict()
            })
        elif user.role == 'admin':
            return jsonify({
                "message": "Admin login successful",
                "role": "admin",
                "user": user.to_dict()
            })
        else:
            return jsonify({"error": "Unknown user role"}), 400
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/updateProfile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    data = request.get_json() or {}

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer profile not found"}), 404

    for attr in ("first_name", "last_name", "email"):
        if attr in data:
            setattr(user, attr, data[attr])

    for attr in ("address", "phone_number", "city", "state", "zip_code", "is_active"):
        if attr in data:
            setattr(customer, attr, data[attr])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not update profile", "details": str(e)}), 500

    return jsonify(customer.to_dict()), 200
