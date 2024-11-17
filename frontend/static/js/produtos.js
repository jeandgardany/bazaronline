// frontend/static/js/produtos.js
class ProdutosManager {
    constructor() {
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Formulário de cadastro
        const form = document.getElementById('formProduto');
        if (form) {
            form.onsubmit = this.handleSubmit.bind(this);
        }
        
        // Filtros
        const filtros = document.querySelectorAll('.filtro');
        filtros.forEach(filtro => {
            filtro.onchange = this.aplicarFiltros.bind(this);
        });
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/api/produtos', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                Toast.show('Produto cadastrado com sucesso!');
                e.target.reset();
            } else {
                throw new Error('Erro ao cadastrar produto');
            }
        } catch (error) {
            Toast.show(error.message, 'error');
        }
    }
    
    aplicarFiltros() {
        const cards = document.querySelectorAll('.produto-card');
        const categoria = document.getElementById('filtroCategoria').value;
        const pesquisa = document.getElementById('pesquisaNome').value.toLowerCase();
        
        cards.forEach(card => {
            const nome = card.dataset.nome.toLowerCase();
            const categoriaCard = card.dataset.categoria;
            const matches = (!categoria || categoriaCard === categoria) && 
                          (!pesquisa || nome.includes(pesquisa));
            
            card.style.display = matches ? 'block' : 'none';
        });
    }
}