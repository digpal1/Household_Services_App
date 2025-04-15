import os

class Config:
    # Database configuration for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hhs_database.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'somesalt')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'librarymanagerjwtsecretkey')
    SECURITY_JOIN_USER_ROLES = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


