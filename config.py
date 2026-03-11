import os


class Config:
    """Application configuration class."""
    
    # Basic settings
    DEBUG = os.environ.get('DEBUG', False)
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings (example)
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
