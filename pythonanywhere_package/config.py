import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fleet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Для PostgreSQL на хостинге
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Настройки безопасности
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Настройки логирования
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
