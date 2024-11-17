# backend/__init__.py
#from flask_sqlalchemy import SQLAlchemy
#import db, get_current_time

# Inicialização do db que será usado em toda a aplicação
#db = SQLAlchemy()

# Versão da aplicação
#__version__ = '1.0.0'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pytz
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração do timezone
    app.config['TIMEZONE'] = pytz.timezone('America/Fortaleza')
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    from .venda_routes import bp as vendas_bp
    app.register_blueprint(vendas_bp, url_prefix='/api/vendas')
    
    return app

def get_current_time():
    """Retorna o horário atual no timezone configurado"""
    return datetime.now(pytz.timezone('America/Fortaleza'))