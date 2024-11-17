# backend/database/init_db.py
from ..models.models import db, Produto, Venda
from .. import create_app
import os

def init_database():
    app = create_app()
    
    with app.app_context():
        # Criar o diretório do banco de dados se não existir
        os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI']), exist_ok=True)
        
        # Criar todas as tabelas
        db.create_all()
        
        # Adicionar alguns produtos de exemplo se o banco estiver vazio
        if not Produto.query.first():
            produtos_exemplo = [
                {
                    'nome': 'Camiseta Básica',
                    'descricao': 'Camiseta 100% algodão',
                    'preco': 29.90,
                    'categoria': 'blusa'
                },
                {
                    'nome': 'Calça Jeans',
                    'descricao': 'Calça jeans tradicional',
                    'preco': 89.90,
                    'categoria': 'calca'
                }
            ]
            
            for produto in produtos_exemplo:
                novo_produto = Produto(**produto)
                db.session.add(novo_produto)
            
            db.session.commit()
            print("Banco de dados inicializado com dados de exemplo!")
        else:
            print("Banco de dados já existe!")

if __name__ == '__main__':
    init_database()