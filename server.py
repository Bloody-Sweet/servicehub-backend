# server.py
from app import create_app, db
from app.models import User, Provider, Service, Booking, Review
import click

app = create_app()

# Provide a shell context for the flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Provider': Provider,
        'Service': Service,
        'Booking': Booking,
        'Review': Review
    }

# Add a custom CLI command to initialize the database (create all tables)
@app.cli.command("init-db")
def init_db():
    """Initialize the database by creating all tables."""
    with app.app_context():
        db.create_all()
        click.echo("Initialized the database (all tables created)!")

if __name__ == '__main__':
    app.run(debug=True)

