from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import db, User, Provider, Service

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


@providers_bp.route('/provider/<int:providerId>/services', methods=['POST'])
def add_service(providerId):
    data = request.json

    provider = Provider.query.filter_by(provider_id=providerId).first()
    if not provider:
        return jsonify({"error": "Provider not found"}), 404

    service_name = data.get('service_name')
    price = data.get('price')

    if not service_name or price is None:
        return jsonify({"error": "Missing required fields: service_name and price"}), 400

    new_service = Service(
        service_name=service_name,
        description=data.get('description'),
        price=price,
        provider_id=provider.provider_id  
    )

    try:
        db.session.add(new_service)
        db.session.commit()
        return jsonify({
            "message": "Service added successfully",
            "service": {
                "id": new_service.service_id,
                "name": new_service.service_name,
                "price": new_service.price,
                "description": new_service.description,
                "provider_id": provider.provider_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add service", "details": str(e)}), 500



@providers_bp.route('/provider/<int:provider_id>/services', methods=['GET'])
def get_provider_services(provider_id):
    provider = Provider.query.filter_by(provider_id=provider_id).first()
    if not provider:
        return jsonify({"error": "Provider not found"}), 404

    services = [
        {
            "service_id": service.service_id,
            "service_name": service.service_name,
            "description": service.description,
            "price": service.price
        }
        for service in provider.services
    ]

    return jsonify({
        "provider_id": provider.provider_id,
        "provider_name": f"{provider.first_name} {provider.last_name}",
        "services": services
    }), 200


@providers_bp.route('/providers/service/<string:service_name>', methods=['GET'])
def get_providers_by_service(service_name):
    
    services = Service.query.filter(Service.service_name.ilike(service_name)).all()

    if not services:
        return jsonify({"message": f"No providers offer {service_name} service."}), 404

    providers_list = []
    for service in services:
        provider = service.provider
        if provider:
            providers_list.append(provider.to_dict())

    return jsonify(providers_list), 200


@providers_bp.route('/provider/<int:provider_id>', methods=['GET'])
def get_provider_with_details(provider_id):
    provider = Provider.query.filter_by(provider_id=provider_id).first()

    if not provider:
        return jsonify({"error": "Provider not found"}), 404

    services = []
    for service in provider.services:
        service_data = {
            "service_id": service.service_id,
            "service_name": service.service_name,
            "description": service.description,
            "price": service.price,
            "subservices": [
                {
                    "service_id":service.service_id,
                    "subservice_id": subservice.subservice_id,
                    "subservice_name": subservice.subservice_name,
                    "price": subservice.price,
                    "status": subservice.status
                }
                for subservice in service.subservices
            ]
        }
        services.append(service_data)

    reviews = [
        {
            "review_id": review.review_id,
            "customer_id": review.customer_id,
            "rating": review.rating,
            "comment": review.comment
        }
        for review in provider.reviews
    ]

    response = {
        "provider": provider.to_dict(),
        "services": services,
        "reviews": reviews
    }

    return jsonify(response), 200
