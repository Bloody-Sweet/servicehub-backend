from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('customer','provider','admin'), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

    def to_dict(self):
        return {
            "user_id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role
        }

class Customer(User):
    __tablename__ = 'customer'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(80))
    city = db.Column(db.String(255)) 
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "customer_id": self.customer_id,
            "address": self.address,
            "phone_number": self.phone_number,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "is_active": self.is_active
        })
        return base

class Provider(User):
    __tablename__ = 'provider'
    
    provider_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    phone_number = db.Column(db.String(80))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    ratings = db.Column(db.Float, default=0.0)
    company_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    services = db.relationship('Service', back_populates='provider', lazy=True)
    bookings = db.relationship('Booking', back_populates='provider', lazy=True)
    reviews = db.relationship('Review', back_populates='provider', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'provider'
    }

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "provider_id": self.provider_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone_number": self.phone_number,
            "ratings": self.ratings,
            "company_name": self.company_name,
            "description": self.description
        })
        return base

class Admin(User):
    __tablename__ = 'admin'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

class Service(db.Model):
    __tablename__ = 'service'
    
    service_id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.provider_id'), nullable=False)
    service_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)

    provider = db.relationship('Provider', back_populates='services')
    bookings = db.relationship('Booking', back_populates='service', lazy=True)
    subservices = db.relationship('Subservice', back_populates='service', lazy=True)  # ✅ New line

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "provider_id": self.provider_id,
            "service_name": self.service_name,
            "description": self.description,
            "price": self.price
        }

class Booking(db.Model):
    __tablename__ = 'booking'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.provider_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)
    service_name = db.Column(db.String(100))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_time = db.Column(db.Time, nullable=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(255)) 
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    note = db.Column(db.String(500))
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    subservice_id = db.Column(db.Integer, db.ForeignKey('subservice.subservice_id'), nullable=False)

    customer = db.relationship('Customer', backref='bookings')
    provider = db.relationship('Provider', back_populates='bookings')
    service = db.relationship('Service', back_populates='bookings')
    review = db.relationship('Review', back_populates='booking', uselist=False)
    
    
    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "provider_id": self.provider_id,
            "service_id": self.service_id,
            "subservice_id": self.subservice_id,
            "service_name": self.service_name,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "booking_time": self.booking_time.strftime('%H:%M:%S') if self.booking_time else None,  
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "note": self.note,
            "total_cost": self.total_cost,
            "status": self.status
        }

class Review(db.Model):
    __tablename__ = 'review'
    
    review_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.provider_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    booking = db.relationship('Booking', back_populates='review')
    customer = db.relationship('Customer', backref='reviews')
    provider = db.relationship('Provider', back_populates='reviews')
    
    def to_dict(self):
        return {
            "review_id": self.review_id,
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "provider_id": self.provider_id,
            "rating": self.rating,
            "comment": self.comment
        }


class Subservice(db.Model):
    __tablename__ = 'subservice'

    subservice_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)
    subservice_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float)
    status = db.Column(db.Boolean, default=True)

    service = db.relationship('Service', back_populates='subservices')
    bookings = db.relationship('Booking', backref='subservice', lazy=True)

    def to_dict(self):
        return {
            "subservice_id": self.subservice_id,
            "service_id": self.service_id,
            "subservice_name": self.subservice_name,
            "price": self.price,
            "status": self.status
        }

