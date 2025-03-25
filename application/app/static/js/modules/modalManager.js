// app/static/js/modules/modalManager.js
export class ModalManager {
    constructor() {
        this.modalElement = document.getElementById('dynamicModal');
        this.modalInstance = new bootstrap.Modal(this.modalElement);
        this.modalContent = this.modalElement.querySelector('.modal-content');
        this.loadingSpinner = this.createLoadingSpinner();
    }

    createLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'd-none text-center p-4';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        return spinner;
    }

    async loadModal(url, options = {}) {
        const {
            method = 'GET',
            data = null,
            onSubmit = null,
            onModalLoaded = null
        } = options;

        try {
            this.showLoading();

            const response = await fetch(url, {
                method,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const content = await response.text();
            this.modalContent.innerHTML = content;

            if (data) {
                this.populateFormData(data);
            }

            if (onModalLoaded) {
                onModalLoaded(this.modalContent);
            }

            if (onSubmit) {
                const form = this.modalContent.querySelector('form');
                if (form) {
                    form.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        await onSubmit(this.getFormData(form));
                    });
                }
            }

            this.modalInstance.show();
        } catch (error) {
            this.showNotification('Hiba', error.message, 'error');
            console.error('Modal loading error:', error);
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loadingSpinner.classList.remove('d-none');
        if (this.modalContent) {
            this.modalContent.appendChild(this.loadingSpinner);
        }
    }

    hideLoading() {
        this.loadingSpinner.classList.add('d-none');
    }

    populateFormData(data) {
        Object.entries(data).forEach(([key, value]) => {
            const element = this.modalContent.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    }

    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Handle empty strings for required fields
            if (value === '' && form.elements[key].hasAttribute('required')) {
                continue;
            }
            data[key] = value;
        }
        
        return data;
    }

    showNotification(title, message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    hide() {
        this.modalInstance.hide();
    }
}