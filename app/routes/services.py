from flask import Blueprint, jsonify
from app.models import Service

services_bp = Blueprint('services', __name__, url_prefix='/api')

@services_bp.route('/services', methods=['GET'])
def list_services():
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services])




