class VendasManager {
    constructor() {
        this.carrinho = new Map();
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('addProdutoForm');
        if (form) {
            form.onsubmit = (e) => {
                e.preventDefault();
                this.adicionarProdutoManualmente();
            };
        }
    }

    adicionarProdutoManualmente() {
        const select = document.getElementById('produtoSelect');
        const quantidadeInput = document.getElementById('quantidade');
        
        if (!select.value) {
            alert('Selecione um produto!');
            return;
        }

        const option = select.selectedOptions[0];
        const quantidade = parseInt(quantidadeInput?.value || 1);
        
        const produto = {
            id: select.value,
            nome: option.dataset.nome,
            preco: parseFloat(option.dataset.preco)
        };

        this.adicionarAoCarrinho(produto, quantidade);
    }

    adicionarAoCarrinho(produto, quantidade = 1) {
        const itemExistente = this.carrinho.get(produto.id);
        
        if (itemExistente) {
            itemExistente.quantidade += quantidade;
        } else {
            this.carrinho.set(produto.id, {
                ...produto,
                quantidade,
                precoUnitario: produto.preco
            });
        }

        this.atualizarCarrinho();
        this.atualizarUIState();
    }

    atualizarCarrinho() {
        const containerCarrinho = document.getElementById('carrinho');
        if (!containerCarrinho) return;

        containerCarrinho.innerHTML = '';
        let total = 0;

        this.carrinho.forEach((item, id) => {
            const itemElement = this.criarElementoCarrinho(item);
            containerCarrinho.appendChild(itemElement);
            total += item.precoUnitario * item.quantidade;
        });

        const subtotalElement = document.getElementById('subtotalCarrinho');
        const totalElement = document.getElementById('totalCarrinho');
        
        if (subtotalElement) {
            subtotalElement.textContent = `R$ ${total.toFixed(2)}`;
        }
        if (totalElement) {
            totalElement.textContent = `R$ ${total.toFixed(2)}`;
        }
    }

    criarElementoCarrinho(item) {
        const div = document.createElement('div');
        div.className = 'cart-item mb-2 p-2 border rounded';
        div.dataset.id = item.id;

        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${item.nome}</strong>
                    <div class="d-flex align-items-center gap-2">
                        <div class="btn-group btn-group-sm">
                            <button type="button" class="btn btn-outline-secondary btn-diminuir">-</button>
                            <span class="px-2 border-top border-bottom py-1">${item.quantidade}</span>
                            <button type="button" class="btn btn-outline-secondary btn-aumentar">+</button>
                        </div>
                        <span class="text-muted">× R$ ${item.precoUnitario.toFixed(2)}</span>
                    </div>
                </div>
                <div class="text-end">
                    <div>R$ ${(item.precoUnitario * item.quantidade).toFixed(2)}</div>
                    <button type="button" class="btn btn-sm btn-outline-danger btn-remover">×</button>
                </div>
            </div>
        `;

        div.querySelector('.btn-diminuir').onclick = () => this.alterarQuantidade(item.id, -1);
        div.querySelector('.btn-aumentar').onclick = () => this.alterarQuantidade(item.id, 1);
        div.querySelector('.btn-remover').onclick = () => this.removerDoCarrinho(item.id);

        return div;
    }

    alterarQuantidade(produtoId, delta) {
        const item = this.carrinho.get(produtoId);
        if (item) {
            const novaQtd = item.quantidade + delta;
            if (novaQtd > 0) {
                item.quantidade = novaQtd;
                this.atualizarCarrinho();
            } else {
                this.removerDoCarrinho(produtoId);
            }
        }
    }

    removerDoCarrinho(produtoId) {
        this.carrinho.delete(produtoId);
        this.atualizarCarrinho();
        this.atualizarUIState();
    }

    atualizarUIState() {
        const itemCount = this.carrinho.size;
        const emptyCart = document.querySelector('.cart-empty');
        const finalizarBtn = document.getElementById('finalizarVenda');
        const cartCount = document.getElementById('cartCount');
        const totalItens = document.getElementById('totalItens');
        
        if (cartCount) cartCount.textContent = itemCount;
        if (totalItens) totalItens.textContent = `${itemCount} ${itemCount === 1 ? 'item' : 'itens'}`;
        if (finalizarBtn) finalizarBtn.disabled = itemCount === 0;
        
        if (emptyCart) {
            if (itemCount === 0) {
                emptyCart.classList.remove('d-none');
            } else {
                emptyCart.classList.add('d-none');
            }
        }
    }

    async finalizarVenda() {
        const btnFinalizar = document.getElementById('finalizarVenda');
        if (!btnFinalizar || this.carrinho.size === 0) return;

        try {
            btnFinalizar.disabled = true;
            btnFinalizar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';

            const vendas = Array.from(this.carrinho.values()).map(item => ({
                produto_id: parseInt(item.id),
                quantidade: item.quantidade,
                valor_total: item.precoUnitario * item.quantidade
            }));

            const response = await fetch('/api/vendas/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(vendas)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro ao finalizar venda');
            }

            const data = await response.json();
            this.showNotification('Sucesso', 'Venda realizada com sucesso!', 'success');
            this.carrinho.clear();
            this.atualizarCarrinho();
            this.atualizarUIState();

        } catch (error) {
            console.error('Erro:', error);
            this.showNotification('Erro', 'Erro ao finalizar venda: ' + error.message, 'danger');
        } finally {
            btnFinalizar.disabled = false;
            btnFinalizar.innerHTML = '<i class="bi bi-check2-circle"></i> Finalizar Venda';
        }
    }

    showNotification(title, message, type = 'success') {
        const toastLiveExample = document.getElementById('notificationToast');
        if (!toastLiveExample) return;

        const toast = new bootstrap.Toast(toastLiveExample, { delay: 3000 });
        document.getElementById('toastTitle').textContent = title;
        document.getElementById('toastMessage').textContent = message;
        toastLiveExample.className = `toast text-bg-${type}`;
        toast.show();
    }
}

// Inicializa o gerenciador de vendas quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    const vendasManager = new VendasManager();
    
    // Adiciona evento ao botão finalizar venda
    const btnFinalizar = document.getElementById('finalizarVenda');
    if (btnFinalizar) {
        btnFinalizar.onclick = () => vendasManager.finalizarVenda();
    }
});