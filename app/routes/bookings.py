from flask import Blueprint, request, jsonify
from app.models import db, Booking

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api')

@bookings_bp.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    user_id = data.get('user_id')
    service_id = data.get('service_id')
    booking = Booking(user_id=user_id, service_id=service_id)
    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Booking created", "booking": booking.to_dict()}), 201

