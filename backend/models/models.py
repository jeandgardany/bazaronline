from datetime import datetime
from backend import db, get_current_time

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float)
    categoria = db.Column(db.String(50))
    codigo_barra = db.Column(db.String(100))
    qr_code = db.Column(db.String(200))
    fotos = db.Column(db.String(500))
    data_cadastro = db.Column(db.DateTime, default=get_current_time)
    
    itens_venda = db.relationship('VendaItem', backref='produto', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'categoria': self.categoria,
            'fotos': self.fotos.split(',') if self.fotos else [],
            'qr_code': self.qr_code,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S')
        }

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, default=get_current_time)
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    itens = db.relationship('VendaItem', backref='venda', lazy=True, cascade='all, delete-orphan')
    
    def calcular_total(self):
        return sum(item.valor_total for item in self.itens)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_venda': self.data_venda.strftime('%Y-%m-%d %H:%M:%S'),
            'total': self.calcular_total(),
            'itens': [item.to_dict() for item in self.itens]
        }

class VendaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id', ondelete='CASCADE'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id', ondelete='RESTRICT'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'produto': self.produto.to_dict(),
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
            'valor_total': self.valor_total
        }