// app/static/js/modules/stockHandler.js
import { ModalManager } from './modalManager.js';

export class StockHandler {
    constructor() {
        this.modalManager = new ModalManager();
        this.historyModal = new bootstrap.Modal(document.getElementById('historyModal'));
        this.emailModal = new bootstrap.Modal(document.getElementById('emailModal'));
        this.templateEditorModal = new bootstrap.Modal(document.getElementById('templateEditorModal'));
        this.medicinesData = null;
        this.selectedMedicines = new Set();

        // this.userFullName = document.getElementById('emailModal')
        //     .querySelector('.email-content')
        //     .innerText
        //     .split('Köszönettel:')[1]
        //     .trim();

        const emailContentElement = document.getElementById('emailContent');
        this.emailTemplate = emailContentElement ? emailContentElement.dataset.template : 
            `Tisztelt Doktornő!

Az alábbi gyógyszereket kérem szépen felírni nekem, hogy ha van rá lehetőség:
{medicines}

Köszönettel:
{fullname}`;
        this.userFullName = document.querySelector('[data-user-fullname]').dataset.userFullname;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('editTemplateBtn')?.addEventListener('click', () => {
            this.showTemplateEditor();
        });

        document.getElementById('saveTemplateBtn')?.addEventListener('click', () => {
            this.saveTemplate();
        });

        document.getElementById('addTransactionBtn')?.addEventListener('click', () => {
            this.handleAddTransaction();
        });

        document.querySelectorAll('.view-history-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleViewHistory(id);
            });
        });

        document.querySelectorAll('.add-transaction-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.closest('button').dataset.id;
                this.handleAddTransaction(id);
            });
        });

        // Checkbox eseménykezelő
        document.querySelectorAll('.medicine-select').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.handleMedicineSelection(e.target);
            });
        });

        // Kiválasztott tételek gomb eseménykezelő
        document.getElementById('showSelectedBtn')?.addEventListener('click', () => {
            this.showSelectedMedicines();
        });

        // Másolás gomb eseménykezelő
        document.getElementById('copyEmailBtn')?.addEventListener('click', () => {
            this.copyEmailToClipboard();
        });
    }

    handleMedicineSelection(checkbox) {
        const showSelectedBtn = document.getElementById('showSelectedBtn');

        if (checkbox.checked) {
            this.selectedMedicines.add({
                id: checkbox.value,
                name: checkbox.dataset.name
            });
        } else {
            this.selectedMedicines.delete([...this.selectedMedicines].find(m => m.id === checkbox.value));
        }

        // Gomb megjelenítése/elrejtése
        showSelectedBtn.style.display = this.selectedMedicines.size > 0 ? 'inline-block' : 'none';
    }

    showSelectedMedicines() {
        const medicinesList = [...this.selectedMedicines]
            .map(m => `- ${m.name}`)
            .join('\n');

        const emailContent = this.emailTemplate
            .replace('{medicines}', medicinesList)
            .replace('{fullname}', this.userFullName);

        document.querySelector('.email-content').innerHTML = emailContent.replace(/\n/g, '<br>');
        this.emailModal.show();
        // const medicinesList = document.getElementById('selectedMedicinesList');
        // medicinesList.innerHTML = [...this.selectedMedicines]
        //     .map(m => `<li>${m.name}</li>`)
        //     .join('');

        // this.emailModal.show();
    }

    async copyEmailToClipboard() {
//         const medicineNames = [...this.selectedMedicines]
//             .map(m => `- ${m.name}`)
//             .join('\n');

//         const emailText = `Tisztelt Doktornő!

// Az alábbi gyógyszereket kérem szépen felírni nekem, hogy ha van rá lehetőség:
// ${medicineNames}

// Köszönettel:
// ${this.userFullName}`;

//         try {
//             await navigator.clipboard.writeText(emailText);
//             this.modalManager.showNotification('Siker', 'Az email szövege a vágólapra másolva!', 'success');
//         } catch (err) {
//             this.modalManager.showNotification('Hiba', 'Nem sikerült a vágólapra másolni!', 'error');
//         }

        const medicinesList = [...this.selectedMedicines]
            .map(m => `- ${m.name}`)
            .join('\n');

        const emailText = this.emailTemplate
            .replace('{medicines}', medicinesList)
            .replace('{fullname}', this.userFullName);

        try {
            await navigator.clipboard.writeText(emailText);
            this.modalManager.showNotification('Siker', 'Az email szövege a vágólapra másolva!', 'success');
        } catch (err) {
            this.modalManager.showNotification('Hiba', 'Nem sikerült a vágólapra másolni!', 'error');
        }
    }

    async handleAddTransaction(medicineId = null) {
        this.modalManager.loadModal('/medicine/stock/modal/transaction', {
            onSubmit: async (formData) => {
                try {
                    if (medicineId) {
                        formData.medicine = medicineId;
                    }

                    const response = await fetch('/medicine/api/stock/transaction', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        },
                        body: JSON.stringify(formData)
                    });

                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(
                            typeof data.error === 'object'
                                ? Object.values(data.error).flat().join('\n')
                                : data.error || 'Hiba történt a mentés során'
                        );
                    }

                    this.modalManager.hide();
                    this.modalManager.showNotification('Siker', 'A tranzakció sikeresen rögzítve!', 'success');
                    location.reload();
                } catch (error) {
                    this.modalManager.showNotification('Hiba', error.message, 'error');
                }
            },
            onModalLoaded: (modalContent) => {
                console.log('Modal loaded');

                // Store medicines data when modal is loaded
                this.medicinesData = window.medicinesData;
                console.log('Stored medicines data:', this.medicinesData);

                // Initialize date picker with current date
                const dateInput = modalContent.querySelector('[name="transaction_date"]');
                if (dateInput) {
                    const now = new Date();
                    dateInput.value = now.toISOString().split('T')[0];
                }

                const medicineSelect = modalContent.querySelector('[name="medicine"]');
                const typeSelect = modalContent.querySelector('[name="transaction_type"]');
                const quantityInput = modalContent.querySelector('[name="quantity"]');

                console.log('Form elements found:', {
                    medicineSelect: !!medicineSelect,
                    typeSelect: !!typeSelect,
                    quantityInput: !!quantityInput
                });

                if (typeSelect && quantityInput && medicineSelect) {
                    // Initial setup
                    this.updateQuantityValidation(typeSelect.value, quantityInput);

                    // Handle transaction type changes
                    typeSelect.addEventListener('change', (e) => {
                        console.log('Type changed:', e.target.value);
                        this.updateQuantityValidation(e.target.value, quantityInput);
                        this.updateDefaultQuantity(e.target.value, medicineSelect, quantityInput);
                    });

                    // Handle medicine selection changes
                    medicineSelect.addEventListener('change', (e) => {
                        console.log('Medicine changed:', e.target.value);
                        this.updateDefaultQuantity(typeSelect.value, medicineSelect, quantityInput);
                    });

                    // Set initial values
                    this.updateDefaultQuantity(typeSelect.value, medicineSelect, quantityInput);
                }
            }
        });
    }

    updateQuantityValidation(transactionType, quantityInput) {
        console.log('Updating quantity validation for type:', transactionType);

        if (transactionType === 'correction') {
            quantityInput.max = 0;
            quantityInput.min = -1000;
            quantityInput.placeholder = 'Add meg a korrekció mennyiségét (negatív szám)';
            quantityInput.value = '';
        } else {
            quantityInput.min = 1;
            quantityInput.max = 1000;
            quantityInput.placeholder = 'Add meg a mennyiséget';
        }
    }

    updateDefaultQuantity(transactionType, medicineSelect, quantityInput) {
        console.log('Updating quantity for:', {
            transactionType,
            medicineId: medicineSelect.value,
            availableData: this.medicinesData
        });

        if (transactionType === 'refill' && medicineSelect.value && this.medicinesData) {
            const medicineData = this.medicinesData[medicineSelect.value];
            console.log('Found medicine data:', medicineData);

            if (medicineData && medicineData.default_packaging) {
                console.log('Setting quantity to:', medicineData.default_packaging);
                quantityInput.value = medicineData.default_packaging;
            }
        } else if (transactionType === 'correction') {
            quantityInput.value = '';
        }
    }

    async handleViewHistory(medicineId) {
        try {
            const response = await fetch(`/medicine/api/stock/history/${medicineId}`);
            if (!response.ok) throw new Error('Nem sikerült betölteni az előzményeket');

            const transactions = await response.json();

            const tbody = document.querySelector('#historyTable tbody');
            if (tbody) {
                tbody.innerHTML = transactions.map(t => `
                    <tr>
                        <td>${t.date}</td>
                        <td>${this.getTransactionTypeLabel(t.type)}</td>
                        <td>${t.quantity}</td>
                        <td>${t.notes || '-'}</td>
                    </tr>
                `).join('');

                if (this.historyModal) {
                    this.historyModal.show();
                }
            }
        } catch (error) {
            this.modalManager.showNotification('Hiba', error.message, 'error');
        }
    }

    getTransactionTypeLabel(type) {
        const types = {
            'initial': 'Kezdő készlet',
            'refill': 'Kiváltás',
            'correction': 'Korrekció'
        };
        return types[type] || type;
    }

    showTemplateEditor() {
        document.getElementById('templateText').value = this.emailTemplate;
        this.emailModal.hide();
        this.templateEditorModal.show();
    }

    async saveTemplate() {
        const newTemplate = document.getElementById('templateText').value;
        
        try {
            const response = await fetch('/medicine/api/email-template', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ template: newTemplate })
            });

            if (!response.ok) throw new Error('Nem sikerült menteni a sablont');

            this.emailTemplate = newTemplate;
            this.templateEditorModal.hide();
            this.showSelectedMedicines(); // Frissítjük az email előnézetet
            this.modalManager.showNotification('Siker', 'A sablon sikeresen mentve!', 'success');
        } catch (error) {
            this.modalManager.showNotification('Hiba', error.message, 'error');
        }
    }
}