// frontend/static/js/utils.js
const Toast = {
    show(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                ${type === 'success' ? '✓' : '⚠'}
            </div>
            <div class="toast-message">${message}</div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
};

const Modal = {
    show(content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="modal-close">&times;</span>
                ${content}
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        modal.querySelector('.modal-close').onclick = () => {
            modal.remove();
        };
        
        return modal;
    }
};

const Api = {
    async get(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro na requisição');
        return response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro na requisição');
        return response.json();
    }
};

const Utils = {
    formatMoney(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
                Toast.show(`Campo ${input.name || 'obrigatório'} não preenchido`, 'error');
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    preventDoubleSubmit(button) {
        if (button.classList.contains('submitting')) return false;
        
        const originalText = button.innerHTML;
        button.classList.add('submitting');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Aguarde...';
        
        setTimeout(() => {
            button.classList.remove('submitting');
            button.disabled = false;
            button.innerHTML = originalText;
        }, 2000);
        
        return true;
    },

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            Toast.show('Copiado para a área de transferência!');
        }).catch(() => {
            Toast.show('Erro ao copiar', 'error');
        });
    }
};

// Event Listeners Globais
document.addEventListener('DOMContentLoaded', () => {
    // Prevenir duplo submit em todos os forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton && !Utils.validateForm(form) || !Utils.preventDoubleSubmit(submitButton)) {
                e.preventDefault();
            }
        });
    });
});