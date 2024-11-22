# backend/app.py
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from backend import db, get_current_time
from datetime import datetime
import os
import pytz


def create_app():
    # Inicialização do Flask
    app = Flask(__name__,
                static_folder='../frontend/static',
                template_folder='../frontend/templates')
        
    # Configurações
    app.config.from_object(Config)
    
    # Garante que o diretório de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicialização das extensões
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Importar modelos
        from models.models import Produto, Venda, VendaItem
      
        # Rotas principais
        @app.route('/')
        def index():
            """Página inicial com listagem de produtos paginados e filtros"""
            page = request.args.get('page', 1, type=int)
            search = request.args.get('search', '').strip()
            category = request.args.get('category', '').strip()
            
            # Query base
            query = Produto.query
            
            # Aplicar filtros
            if search:
                query = query.filter(Produto.nome.ilike(f'%{search}%'))
            if category:
                query = query.filter(Produto.categoria.ilike(category))
            
            # Ordenar e paginar
            produtos = (query
                       .order_by(Produto.data_cadastro.desc())
                       .paginate(page=page, per_page=9, error_out=False))
            
            return render_template('index.html', produtos=produtos)
        
        @app.route('/cadastrar')
        def cadastrar():
            """Página de cadastro de produtos"""
            categorias = ['blusas', 'calcas', 'vestidos', 'croppeds', 'regatas', 'camisas', 'variadas']
            return render_template('produtos/cadastrar.html', categorias=categorias)
            
        @app.route('/vendas')
        def vendas():
            """Página de realização de vendas"""
            produtos = Produto.query.filter(Produto.preco.isnot(None)).order_by(Produto.nome).all()
            return render_template('vendas/realizar_venda.html', produtos=produtos)
        
        @app.route('/produtos')
        def produtos():
            """Página de listagem de produtos"""
            produtos = Produto.query.order_by(Produto.nome).all()
            return render_template('produtos/listar.html', produtos=produtos)
        
        @app.route('/editar/<int:id>')
        def editar_produto(id):
            """Página de edição de produto"""
            produto = Produto.query.get_or_404(id)
            categorias = ['blusas', 'calcas', 'vestidos', 'croppeds', 'regatas', 'camisas', 'variadas']
            return render_template('produtos/editar.html', 
                                produto=produto,
                                categorias=categorias)
  
        @app.route('/historico')
        def historico():
            """Página de histórico de vendas"""
            vendas = (Venda.query
                     .order_by(Venda.data_venda.desc())
                     .all())
            total_hoje = sum(v.total for v in vendas 
                           if v.data_venda.date() == datetime.now().date())
            total_mes = sum(v.total for v in vendas 
                          if v.data_venda.month == datetime.now().month)
            
            return render_template('vendas/historico.html',
                                 vendas=vendas,
                                 total_hoje=total_hoje,
                                 total_mes=total_mes)

        @app.route('/venda/<int:id>')
        def detalhe_venda(id):
            """Página de detalhes de uma venda específica"""
            venda = Venda.query.get_or_404(id)
            return render_template('vendas/detalhe.html', venda=venda)
        
        # Tratamento de erros
        @app.errorhandler(404)
        def pagina_nao_encontrada(e):
            return render_template('errors/404.html'), 404
        
        @app.errorhandler(500)
        def erro_interno(e):
            db.session.rollback()
            return render_template('errors/500.html'), 500
        
        # Importar e registrar blueprints
        from produto_routes import bp as produto_bp
        from venda_routes import bp as venda_bp
        
        app.register_blueprint(produto_bp, url_prefix='/api/produtos')
        app.register_blueprint(venda_bp, url_prefix='/api/vendas')
        
        # Criar banco de dados
        db.create_all()
        
        # Configurações de segurança adicionais
        @app.after_request
        def after_request(response):
            response.headers.add('X-Content-Type-Options', 'nosniff')
            response.headers.add('X-Frame-Options', 'DENY')
            response.headers.add('X-XSS-Protection', '1; mode=block')
            return response
        
        return app

def init_db():
    """Inicializa o banco de dados com dados iniciais se necessário"""
    with create_app().app_context():
        from models.models import Produto, Venda, VendaItem
        db.create_all()
        
        # Você pode adicionar dados iniciais aqui se desejar
        if not Produto.query.first():
            categorias_exemplo = ['blusa', 'calca', 'vestido']
            for cat in categorias_exemplo:
                produto = Produto(
                    nome=f'Exemplo {cat}',
                    categoria=cat,
                    preco=99.90
                )
                db.session.add(produto)
            db.session.commit()
