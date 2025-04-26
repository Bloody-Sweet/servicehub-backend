from flask import Blueprint, request, jsonify
from app.models import db, Review

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api')

@reviews_bp.route('/createReview', methods=['POST'])
def create_review():
    data = request.json

    booking_id = data.get('booking_id')
    customer_id = data.get('customer_id')
    provider_id = data.get('provider_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([booking_id, customer_id, provider_id, rating]):
        return jsonify({"error": "Missing required fields"}), 400

    review = Review(
        booking_id=booking_id,
        customer_id=customer_id,
        provider_id=provider_id,
        rating=rating,
        comment=comment
    )

    try:
        db.session.add(review)
        db.session.commit()
        return jsonify({"message": "Review created successfully", "review": review.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create review", "details": str(e)}), 500
    


@reviews_bp.route('/reviews/provider/<int:provider_id>', methods=['GET'])
def get_reviews_by_provider(provider_id):
    reviews = Review.query.filter_by(provider_id=provider_id).all()
    
    if not reviews:
        return jsonify({"message": "No reviews found for this provider."}), 404

    return jsonify([review.to_dict() for review in reviews]), 200

