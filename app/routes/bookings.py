from flask import Blueprint, request, jsonify
from app.models import db, Booking

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api')

@bookings_bp.route('/createbooking', methods=['POST'])
def create_booking():
    data = request.json

    customer_id = data.get('customer_id')
    provider_id = data.get('provider_id')
    service_id = data.get('service_id')
    service_name = data.get('service_name')
    booking_time = data.get('booking_time')
    address = data.get('address')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')
    note = data.get('note')
    total_cost = data.get('total_cost')
    status = data.get('status', 'pending')  

    # Basic validation
    if not all([customer_id, provider_id, service_id, address, city, state, zip_code, total_cost, service_name, booking_time]):
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
        status=status
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
    return jsonify([b.to_dict() for b in bookings]), 200


@bookings_bp.route('/bookings/provider/<int:provider_id>', methods=['GET'])
def get_bookings_by_provider(provider_id):
    bookings = Booking.query.filter_by(provider_id=provider_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@bookings_bp.route('/bookings/service/<int:service_id>', methods=['GET'])
def get_bookings_by_service(service_id):
    bookings = Booking.query.filter_by(service_id=service_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@bookings_bp.route('/getAllBookings', methods=['GET'])
def get_all_bookings():
    bookings = Booking.query.all()
    return jsonify([b.to_dict() for b in bookings]), 200
