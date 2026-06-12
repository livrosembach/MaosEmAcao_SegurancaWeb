// opportunities.js
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchOpportunity');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            console.log('Searching for:', e.target.value);
            // Implement search logic here
        });
    }
});