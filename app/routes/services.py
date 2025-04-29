from flask import Blueprint, jsonify, request
from app.models import db, User, Provider, Service, Subservice, Customer

services_bp = Blueprint('services', __name__, url_prefix='/api')

@services_bp.route('/services', methods=['GET'])
def list_services():
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services])

@services_bp.route('/subservices', methods=['POST'])
def create_subservice():
    data = request.json
    service_id = data.get('service_id')
    subservice_name = data.get('subservice_name')
    price = data.get('price')

    if not all([service_id, subservice_name]):
        return jsonify({"error": "Missing required fields"}), 400

    subservice = Subservice(
        service_id=service_id,
        subservice_name=subservice_name,
        price=price
    )

    try:
        db.session.add(subservice)
        db.session.commit()
        return jsonify({"message": "Subservice created successfully", "subservice": subservice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create subservice", "details": str(e)}), 500


@services_bp.route('/allSubServices', methods=['GET'])
def get_all_subservices():
    try:
        subservices = Subservice.query.all()

        if not subservices:
            return jsonify({"message": "No subservices found."}), 404

        return jsonify([subservice.to_dict() for subservice in subservices]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@services_bp.route('/subservices/<int:service_id>', methods=['GET'])
def get_subservices_by_service(service_id):
    try:
        subservices = Subservice.query.filter_by(service_id=service_id).all()

        if not subservices:
            return jsonify({"message": "No subservices found for the given service ID."}), 404

        return jsonify([subservice.to_dict() for subservice in subservices]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@services_bp.route('/updateservice', methods=['PUT'])
def update_service_and_subservices():
    data = request.get_json()

    action = data.get('action') 
    service_id = data.get('service_id')
    service_name = data.get('service_name')
    description = data.get('description')
    price = data.get('price')
    subservices = data.get('subservices', [])

    if action == 'add':
        new_service = Service(
            service_name=service_name,
            description=description,
            price=price,
            provider_id=data.get('provider_id')  
        )
        db.session.add(new_service)
        db.session.commit()  
        
        for sub in subservices:
            new_sub = Subservice(
                service_id=new_service.service_id,
                subservice_name=sub.get('subservice_name'),
                price=sub.get('price'),
                status=1
            )
            db.session.add(new_sub)

        db.session.commit()

        return jsonify({"message": "Service and Subservices added successfully!"}), 201

    elif action == 'update':
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"message": "Service not found."}), 404

        service.service_name = service_name
        service.description = description
        service.price = price

        for sub in subservices:
            subservice_id = sub.get('subservice_id')
            subservice_name = sub.get('subservice_name')
            sub_price = sub.get('price')
            sub_status = sub.get('status')

            if subservice_id:
                existing_sub = Subservice.query.get(subservice_id)
                if existing_sub:
                    existing_sub.subservice_name = subservice_name
                    existing_sub.price = sub_price
                    existing_sub.status = sub_status
            else:
                new_sub = Subservice(
                    service_id=service_id,
                    subservice_name=subservice_name,
                    price=sub_price,
                    status=1
                )
                db.session.add(new_sub)

        db.session.commit()

        return jsonify({"message": "Service and Subservices updated successfully!"}), 200

    else:
        return jsonify({"message": "Invalid action provided."}), 400
    
    
@services_bp.route("/updateProfile/<int:user_id>", methods=["PUT"])
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
