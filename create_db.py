from app import create_app
from app.models import db, Booking, Review, Subservice

app = create_app()

with app.app_context():
    db.create_all()
    # Booking.__table__.create(db.engine, checkfirst=True)
    # Review.__table__.create(db.engine, checkfirst=True)
    # Subservice.__table__.create(db.engine, checkfirst=True)
    print("All tables created successfully.")
