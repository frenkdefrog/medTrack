// app/static/js/modules/medicineHandler.js
import { ModalManager } from './modalManager.js';
import { SuggestionManager } from './suggestionManager.js';

export class MedicineHandler {
    constructor() {
        this.modalManager = new ModalManager();
        this.initializeEventListeners();
        this.initializeTooltips();
    }

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initializeEventListeners() {
        document.getElementById('addMedicineBtn')?.addEventListener('click', () => {
            this.handleAddMedicine();
        });

        document.querySelectorAll('.edit-medicine-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleEditMedicine(id);
            });
        });

        document.querySelectorAll('.delete-medicine-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleDeleteMedicine(id);
            });
        });
    }

    async handleAddMedicine() {
        this.modalManager.loadModal('/medicine/modal/add', {
            onModalLoaded: (modalContent) => {
                const form = modalContent.querySelector('form');
                if(form) {
                    new SuggestionManager(form);
                }
            },
            onSubmit: async (formData) => {
                try {
                    const response = await fetch('/medicine/api/medicines', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        },
                        body: JSON.stringify(formData)
                    });

                    if (!response.ok) {
                        const data = await response.json();
                        throw new Error(data.error || 'Hiba történt a mentés során');
                    }

                    this.modalManager.hide();
                    this.modalManager.showNotification('Siker', 'A gyógyszer sikeresen hozzáadva!', 'success');
                    location.reload();
                } catch (error) {
                    this.modalManager.showNotification('Hiba', error.message, 'error');
                }
            }
        });
    }

    async handleEditMedicine(medicineId) {
        try {
            const response = await fetch(`/medicine/api/medicines/${medicineId}`);
            if (!response.ok) throw new Error('Nem sikerült betölteni a gyógyszer adatait');
            
            const medicineData = await response.json();

            this.modalManager.loadModal(`/medicine/modal/edit?id=${medicineId}`, {
                data: medicineData,
                onModalLoaded: (modalContent)=> {
                    const form = modalContent.querySelector('form');
                    if (form) {
                        new SuggestionManager(form);
                    }
                },
                onSubmit: async (formData) => {
                    try {
                        const updateResponse = await fetch(`/medicine/api/medicines/${medicineId}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                            },
                            body: JSON.stringify(formData)
                        });

                        if (!updateResponse.ok) {
                            const data = await updateResponse.json();
                            throw new Error(data.error || 'Hiba történt a mentés során');
                        }

                        this.modalManager.hide();
                        this.modalManager.showNotification('Siker', 'A gyógyszer sikeresen módosítva!', 'success');
                        location.reload();
                    } catch (error) {
                        this.modalManager.showNotification('Hiba', error.message, 'error');
                    }
                }
            });
        } catch (error) {
            this.modalManager.showNotification('Hiba', error.message, 'error');
        }
    }

    async handleDeleteMedicine(medicineId) {
        if (confirm('Biztosan törölni szeretné ezt a gyógyszert?')) {
            try {
                const response = await fetch(`/medicine/api/medicines/${medicineId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });

                if (!response.ok) throw new Error('Hiba történt a törlés során');

                this.modalManager.showNotification('Siker', 'A gyógyszer sikeresen törölve!', 'success');
                location.reload();
            } catch (error) {
                this.modalManager.showNotification('Hiba', error.message, 'error');
            }
        }
    }
}