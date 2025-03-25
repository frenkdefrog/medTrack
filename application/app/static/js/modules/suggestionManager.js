// app/static/js/modules/suggestionManager.js
export class SuggestionManager {
  constructor(formElement) {
      this.form = formElement;
      this.hasSuggestionCheckbox = this.form.querySelector('#has_suggestion');
      this.suggestionSelectDiv = this.form.querySelector('#suggestionSelectDiv');
      this.suggestionSelect = this.form.querySelector('#suggestion_id');
      
      this.initialize();
  }

  initialize() {
      if (!this.hasSuggestionCheckbox || !this.suggestionSelectDiv) return;

      // Set initial state
      this.updateSelectVisibility();

      // Add event listener
      this.hasSuggestionCheckbox.addEventListener('change', () => {
          this.updateSelectVisibility();
      });
  }

  updateSelectVisibility() {
      if (this.hasSuggestionCheckbox.checked) {
          this.suggestionSelectDiv.style.display = 'block';
      } else {
          this.suggestionSelectDiv.style.display = 'none';
          if (this.suggestionSelect) {
              this.suggestionSelect.value = '';
          }
      }
  }
}