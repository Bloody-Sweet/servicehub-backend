from flask import Blueprint, request, jsonify
from app.models import db, Booking, Subservice, Provider, User, Customer, Service
from sqlalchemy import func

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api')

@bookings_bp.route('/createbooking', methods=['POST'])
def create_booking():
    data = request.json

    customer_id = data.get('customer_id')
    provider_id = data.get('provider_id')
    service_id = data.get('service_id')
    subservice_id =  data.get('subservice_id')
    service_name = data.get('service_name')
    booking_time = data.get('booking_time')
    address = data.get('address')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')
    note = data.get('note')
    total_cost = data.get('total_cost')
    status = data.get('status', 'pending')  

    if not all([customer_id, provider_id, service_id, address, city, state, zip_code, total_cost, service_name, booking_time, subservice_id]):
        return jsonify({"error": "Missing required fields"}), 400

    booking = Booking(
        customer_id=customer_id,
        provider_id=provider_id,
        service_id=service_id,
        service_name=service_name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        note=note,
        total_cost=total_cost,
        status=status,
        subservice_id=subservice_id
    )
    
    if booking_time:
            from datetime import datetime
            booking.booking_time = datetime.strptime(booking_time, "%H:%M:%S").time()

    try:
        db.session.add(booking)
        db.session.commit()
        return jsonify({
            "message": "Booking created successfully",
            "booking": booking.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to create booking",
            "details": str(e)
        }), 500


@bookings_bp.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        return jsonify(booking.to_dict()), 200
    else:
        return jsonify({"error": "Booking not found"}), 404


@bookings_bp.route('/bookings/customer/<int:customer_id>', methods=['GET'])
def get_bookings_by_customer(customer_id):
    bookings = Booking.query.filter_by(customer_id=customer_id).all()
    results = []

    for booking in bookings:
   
        provider = Provider.query.filter_by(provider_id=booking.provider_id).first()
        if provider:
            user = User.query.filter_by(id=provider.user_id).first()
            provider_name = user.first_name if user else "Unknown Provider"
        else:
            provider_name = "Unknown Provider"

        booking_data = booking.to_dict() 
        booking_data['provider_name'] = provider_name    
        results.append(booking_data)

    return jsonify(results), 200

@bookings_bp.route('/bookings/provider/<int:provider_id>', methods=['GET'])
def get_bookings_by_provider(provider_id):
    bookings = Booking.query.filter_by(provider_id=provider_id).all()
    results = []

    for booking in bookings:
  
        customer = Customer.query.filter_by(customer_id=booking.customer_id).first()
        if customer:
            user = User.query.filter_by(id=customer.user_id).first()
            if user:
                customer_name = f"{user.first_name} {user.last_name}"
            else:
                customer_name = "Unknown Customer"
        else:
            customer_name = "Unknown Customer"

        booking_data = booking.to_dict()
        booking_data['customer_name'] = customer_name
        results.append(booking_data)

    return jsonify(results), 200

@bookings_bp.route('/bookings/service/<int:service_id>', methods=['GET'])
def get_bookings_by_service(service_id):
    bookings = Booking.query.filter_by(service_id=service_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@bookings_bp.route('/getAllBookings', methods=['GET'])
def get_all_bookings():
    bookings = Booking.query.all()
    return jsonify([b.to_dict() for b in bookings]), 200


@bookings_bp.route('/updatebooking', methods=['PUT'])
def update_booking():
    data = request.get_json()
    print("service name", data)

    if not data or 'booking_id' not in data:
        return jsonify({"error": "Booking ID is required."}), 400

    booking_id = data['booking_id']
    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    allowed_fields = [
        "customer_id", "provider_id", "service_id", "service_name", "subservice_id",
        "address", "city", "state", "zip_code", "note", "total_cost",
        "booking_time", "booking_date", "status"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(booking, field, data[field])

    db.session.commit()

    return jsonify({"message": "Booking updated successfully.", "booking": booking.to_dict()}), 200


@bookings_bp.route('/bookings/withCustomer', methods=['GET'])
def get_bookings_with_customer():
    bookings = Booking.query.all()
    results = []

    for booking in bookings:
        customer = Customer.query.filter_by(customer_id=booking.customer_id).first()

        customer_name = ""
        if customer:
            user = User.query.filter_by(id=customer.user_id).first()
            customer_name = user.first_name if user else "Unknown Customer"

        booking_data = booking.to_dict()
        booking_data['customer_name'] = customer_name

        results.append(booking_data)

    return jsonify(results), 200

@bookings_bp.route('/performance', methods=['GET'])
def get_service_performance():
    try:
        services = Service.query.all()

        if not services:
            return jsonify({"message": "No services found."}), 404

        result = []

        total_revenue = db.session.query(func.sum(Booking.total_cost)).scalar() or 0

        if total_revenue == 0:
            return jsonify({"message": "No bookings found."}), 404

        for service in services:
            service_revenue = (
                db.session.query(func.sum(Booking.total_cost))
                .filter(Booking.service_id == service.service_id)
                .scalar()
            ) or 0

            performance_percentage = (service_revenue / total_revenue) * 100

            result.append({
                "service_name": service.service_name,
                "performance": round(performance_percentage, 2)
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": "Something went wrong.", "error": str(e)}), 500