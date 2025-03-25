// app/static/js/modules/recommendationHandler.js
import { ModalManager } from './modalManager.js';

export class RecommendationHandler {
    constructor() {
        this.modalManager = new ModalManager();
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('addRecommendationBtn')?.addEventListener('click', () => {
            this.handleAddRecommendation();
        });

        document.querySelectorAll('.edit-recommendation-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleEditRecommendation(id);
            });
        });

        document.querySelectorAll('.delete-recommendation-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleDeleteRecommendation(id);
            });
        });
    }

    async handleAddRecommendation() {
        this.modalManager.loadModal('/recoms/modal/add', {
            onSubmit: async (formData) => {
                try {
                    const response = await fetch('/recoms/api/recommendations', {
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
                    this.modalManager.showNotification('Siker', 'A javaslat sikeresen hozzáadva!', 'success');
                    location.reload();
                } catch (error) {
                    this.modalManager.showNotification('Hiba', error.message, 'error');
                }
            }
        });
    }

    async handleEditRecommendation(recommendationId) {
        try {
            const response = await fetch(`/recoms/api/recommendations/${recommendationId}`);
            if (!response.ok) throw new Error('Nem sikerült betölteni a javaslat adatait');
            
            const recommendationData = await response.json();

            this.modalManager.loadModal(`/recoms/modal/edit?id=${recommendationId}`, {
                data: recommendationData,
                onSubmit: async (formData) => {
                    try {
                        const updateResponse = await fetch(`/recoms/api/recommendations/${recommendationId}`, {
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
                        this.modalManager.showNotification('Siker', 'A javaslat sikeresen módosítva!', 'success');
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

    async handleDeleteRecommendation(recommendationId) {
        if (confirm('Biztosan törölni szeretné ezt a javaslatot?')) {
            try {
                const response = await fetch(`/recoms/api/recommendations/${recommendationId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });

                if (!response.ok) throw new Error('Hiba történt a törlés során');

                this.modalManager.showNotification('Siker', 'A javaslat sikeresen törölve!', 'success');
                location.reload();
            } catch (error) {
                this.modalManager.showNotification('Hiba', error.message, 'error');
            }
        }
    }
}