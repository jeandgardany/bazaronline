from flask import Blueprint, jsonify, request
from backend import db, get_current_time
from models.models import Venda, VendaItem, Produto
from datetime import datetime
from sqlalchemy import func
import pytz

bp = Blueprint('vendas', __name__)

@bp.route('/create', methods=['POST'])
def criar_venda():
    try:
        itens_venda = request.json
        if not itens_venda:
            return jsonify({'error': 'Nenhum item fornecido'}), 400

        venda = Venda()
        db.session.add(venda)
        
        for item in itens_venda:
            produto = Produto.query.get(item['produto_id'])
            if not produto:
                return jsonify({'error': f'Produto {item["produto_id"]} não encontrado'}), 404
                
            item_venda = VendaItem(
                venda=venda,
                produto=produto,
                quantidade=item['quantidade'],
                preco_unitario=produto.preco,
                valor_total=produto.preco * item['quantidade']
            )
            db.session.add(item_venda)
        
        venda.total = sum(item.valor_total for item in venda.itens)
        
        db.session.commit()
        return jsonify(venda.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/update/<int:id>', methods=['PUT'])
def atualizar_venda(id):
    try:
        venda = Venda.query.get_or_404(id)
        itens_venda = request.json

        # Remove itens existentes
        for item in venda.itens:
            db.session.delete(item)

        # Adiciona novos itens
        for item in itens_venda:
            produto = Produto.query.get(item['produto_id'])
            if not produto:
                return jsonify({'error': f'Produto {item["produto_id"]} não encontrado'}), 404

            item_venda = VendaItem(
                venda=venda,
                produto=produto,
                quantidade=item['quantidade'],
                preco_unitario=produto.preco,
                valor_total=produto.preco * item['quantidade']
            )
            db.session.add(item_venda)

        venda.total = sum(item.valor_total for item in venda.itens)
        db.session.commit()
        
        return jsonify(venda.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/delete/<int:id>', methods=['DELETE'])
def excluir_venda(id):
    try:
        venda = Venda.query.get_or_404(id)
        db.session.delete(venda)
        db.session.commit()
        return jsonify({'message': 'Venda excluída com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/historico/<periodo>', methods=['GET'])
def listar_vendas(periodo):
    try:
        tz = pytz.timezone('America/Fortaleza')
        hoje = datetime.now(tz).date()
        
        if periodo == 'hoje':
            data_inicio = hoje
        elif periodo == 'mes':
            data_inicio = hoje.replace(day=1)
        elif periodo == 'ano':
            data_inicio = hoje.replace(month=1, day=1)
        else:
            return jsonify({'error': 'Período inválido'}), 400
            
        vendas = Venda.query.filter(
            func.date(Venda.data_venda) >= data_inicio
        ).order_by(Venda.data_venda.desc()).all()
        
        return jsonify([venda.to_dict() for venda in vendas])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/historico/<int:id>', methods=['GET'])
def obter_venda(id):
    try:
        venda = Venda.query.get_or_404(id)
        return jsonify(venda.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/resumo', methods=['GET'])
def obter_resumo():
    try:
        tz = pytz.timezone('America/Fortaleza')
        hoje = datetime.now(tz).date()
        inicio_mes = hoje.replace(day=1)
        
        # Total de hoje usando timezone correto
        vendas_hoje = Venda.query.filter(
            func.date(Venda.data_venda) == hoje
        ).all()
        total_hoje = sum(venda.total for venda in vendas_hoje)
        
        # Total do mês
        vendas_mes = Venda.query.filter(
            func.date(Venda.data_venda) >= inicio_mes
        ).all()
        total_mes = sum(venda.total for venda in vendas_mes)
        
        # Quantidade total de vendas
        quantidade = Venda.query.count()
        
        # Ticket médio
        ticket_medio = total_mes / len(vendas_mes) if vendas_mes else 0
        
        return jsonify({
            'totalHoje': total_hoje,
            'totalMes': total_mes,
            'quantidade': quantidade,
            'ticketMedio': ticket_medio
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400