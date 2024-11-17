# backend/config.py
import os

class Config:
    # Configurações básicas
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database/bazar.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'seu-secret-key-seguro'
    
    # Configurações do servidor
    HOST = '0.0.0.0'
    PORT = 8005
    DEBUG = True
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'frontend/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}