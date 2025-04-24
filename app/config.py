import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:root@localhost:3306/servicehub'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

