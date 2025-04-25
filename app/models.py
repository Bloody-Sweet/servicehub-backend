from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('customer','provider','admin'), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role
        }

# -----------------------------
# Subtype tables using JOINED inheritance
# -----------------------------

class Customer(User):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
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

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    ratings = db.Column(db.Float, default=0.0)
    company_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': 'provider'
    }

    def to_dict(self):
        base = super().to_dict()
        base.update({
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

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

# -----------------------------
# Other tables
# -----------------------------

class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    provider = db.relationship('Provider', backref=db.backref('services', lazy=True))



class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')

    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))

   

class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    booking = db.relationship('Booking', backref=db.backref('review', uselist=False))

