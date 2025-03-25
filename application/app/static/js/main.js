// app/static/js/main.js
import { MedicineHandler } from './modules/medicineHandler.js';
import { RecommendationHandler } from './modules/recommendationHandler.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize handlers based on current page
    if (document.querySelector('.medicine-page')) {
        new MedicineHandler();
    }
    if (document.querySelector('.recommendation-page')) {
        new RecommendationHandler();
    }
});