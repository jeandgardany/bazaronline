import json
from datetime import datetime
from backend import db
from backend.models.models import Produto, Venda, VendaItem

def backup_dados():
    """Faz backup dos dados existentes"""
    dados = {
        'produtos': [],
        'vendas': [],
        'venda_itens': []
    }
    
    # Backup de produtos
    produtos = Produto.query.all()
    for p in produtos:
        dados['produtos'].append({
            'id': p.id,
            'nome': p.nome,
            'descricao': p.descricao,
            'preco': p.preco,
            'categoria': p.categoria,
            'codigo_barra': p.codigo_barra,
            'qr_code': p.qr_code,
            'fotos': p.fotos,
            'data_cadastro': p.data_cadastro.isoformat() if p.data_cadastro else None
        })
    
    # Backup de vendas
    vendas = Venda.query.all()
    for v in vendas:
        dados['vendas'].append({
            'id': v.id,
            'data_venda': v.data_venda.isoformat() if v.data_venda else None,
            'total': v.total
        })
    
    # Backup de itens de venda
    itens = VendaItem.query.all()
    for i in itens:
        dados['venda_itens'].append({
            'id': i.id,
            'venda_id': i.venda_id,
            'produto_id': i.produto_id,
            'quantidade': i.quantidade,
            'preco_unitario': i.preco_unitario,
            'valor_total': i.valor_total
        })
    
    # Salvar backup em arquivo
    with open('backup_dados.json', 'w') as f:
        json.dump(dados, f, indent=2)
    
    return dados

def restaurar_dados(dados):
    """Restaura os dados do backup"""
    try:
        # Restaurar produtos
        for p_data in dados['produtos']:
            produto = Produto(
                id=p_data['id'],
                nome=p_data['nome'],
                descricao=p_data['descricao'],
                preco=p_data['preco'],
                categoria=p_data['categoria'],
                codigo_barra=p_data['codigo_barra'],
                qr_code=p_data['qr_code'],
                fotos=p_data['fotos'],
                data_cadastro=datetime.fromisoformat(p_data['data_cadastro']) if p_data['data_cadastro'] else None,
                # Novos campos com valores padrão
                preco_custo=p_data['preco'] * 0.7 if p_data['preco'] else None,  # 30% de margem estimada
                quantidade_estoque=0,
                quantidade_minima=5
            )
            db.session.add(produto)
        
        # Restaurar vendas
        for v_data in dados['vendas']:
            venda = Venda(
                id=v_data['id'],
                data_venda=datetime.fromisoformat(v_data['data_venda']) if v_data['data_venda'] else None,
                total=v_data['total'],
                # Novos campos com valores padrão
                forma_pagamento='dinheiro',
                parcelas=1
            )
            db.session.add(venda)
        
        # Restaurar itens de venda
        for i_data in dados['venda_itens']:
            item = VendaItem(
                id=i_data['id'],
                venda_id=i_data['venda_id'],
                produto_id=i_data['produto_id'],
                quantidade=i_data['quantidade'],
                preco_unitario=i_data['preco_unitario'],
                valor_total=i_data['valor_total']
            )
            db.session.add(item)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao restaurar dados: {str(e)}")
        return False

def migrar_dados():
    """Executa o processo completo de migração"""
    try:
        print("Iniciando backup dos dados...")
        dados = backup_dados()
        
        print("Limpando banco de dados...")
        db.drop_all()
        db.create_all()
        
        print("Restaurando dados...")
        if restaurar_dados(dados):
            print("Migração concluída com sucesso!")
            return True
        else:
            print("Erro na restauração dos dados!")
            return False
            
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False