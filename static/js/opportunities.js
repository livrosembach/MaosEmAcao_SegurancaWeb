// opportunities.js
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchOpportunity');
    const cards = document.querySelectorAll('[data-opportunity-card]');

    if (searchInput && cards.length > 0) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();

            cards.forEach((card) => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});
