from flask import Blueprint, request, jsonify
from app.models import db, Review

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api')

@reviews_bp.route('/reviews', methods=['POST'])
def submit_review():
    data = request.json
    booking_id = data.get('booking_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    review = Review(booking_id=booking_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review submitted", "review": review.to_dict()}), 201

