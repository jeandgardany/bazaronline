# backend/produto_routes.py
from flask import Blueprint, request, jsonify, current_app
import os
from app import db
from models.models import Produto
from helpers import save_file, gerar_qr_code

bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')

@bp.route('/', methods=['GET'])
def listar_produtos():
    produtos = Produto.query.all()
    return jsonify([produto.to_dict() for produto in produtos])

@bp.route('/<int:id>', methods=['GET'])
def obter_produto(id):
    produto = Produto.query.get_or_404(id)
    return jsonify(produto.to_dict())

@bp.route('/', methods=['POST'])
def criar_produto():
    try:
        data = request.form.to_dict()
        fotos = request.files.getlist('fotos')
        
        # Salvar fotos
        foto_paths = []
        for foto in fotos:
            filename = save_file(foto)
            if filename:
                foto_paths.append(filename)
        
        produto = Produto(
            nome=data['nome'],
            descricao=data['descricao'],
            preco=float(data['preco']) if data['preco'] else None,
            categoria=data['categoria'],
            fotos=','.join(foto_paths)
        )
        
        db.session.add(produto)
        db.session.commit()
        
        # Gerar QR Code após ter o ID
        qr_data = f"produto_id:{produto.id}|nome:{produto.nome}|preco:{produto.preco}"
        produto.qr_code = gerar_qr_code(qr_data)
        
        db.session.commit()
        
        return jsonify(produto.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    try:
        produto = Produto.query.get_or_404(id)
        data = request.form.to_dict()
        
        produto.nome = data.get('nome', produto.nome)
        produto.descricao = data.get('descricao', produto.descricao)
        produto.preco = float(data['preco']) if data.get('preco') else produto.preco
        produto.categoria = data.get('categoria', produto.categoria)
        
        if 'fotos' in request.files:
            fotos = request.files.getlist('fotos')
            foto_paths = []
            
            if produto.fotos:
                for foto_antiga in produto.fotos.split(','):
                    try:
                        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], foto_antiga))
                    except:
                        pass
            
            for foto in fotos:
                filename = save_file(foto)
                if filename:
                    foto_paths.append(filename)
            
            produto.fotos = ','.join(foto_paths)
        
        qr_data = f"produto_id:{produto.id}|nome:{produto.nome}|preco:{produto.preco}"
        produto.qr_code = gerar_qr_code(qr_data)
        
        db.session.commit()
        return jsonify(produto.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>', methods=['DELETE'])
def excluir_produto(id):
    try:
        produto = Produto.query.get_or_404(id)
        
        if produto.fotos:
            for foto in produto.fotos.split(','):
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], foto))
                except:
                    pass
        
        db.session.delete(produto)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400