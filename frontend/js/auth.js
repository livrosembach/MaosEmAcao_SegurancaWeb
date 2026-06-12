// auth.js
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Mock authentication
            const email = document.getElementById('email').value;
            if (email.includes('admin')) {
                window.location.href = 'admin-dashboard.html';
            } else if (email.includes('ong')) {
                window.location.href = 'ngo-dashboard.html';
            } else {
                window.location.href = 'volunteer-dashboard.html';
            }
        });
    }

    const toggleProfiles = document.querySelectorAll('.profile-toggle');
    if (toggleProfiles.length > 0) {
        const ngoForm = document.getElementById('ngo-form');
        const volForm = document.getElementById('volunteer-form');
        
        toggleProfiles.forEach(btn => {
            btn.addEventListener('click', () => {
                toggleProfiles.forEach(b => b.classList.remove('btn-primary'));
                toggleProfiles.forEach(b => b.classList.add('btn-secondary'));
                
                btn.classList.add('btn-primary');
                btn.classList.remove('btn-secondary');
                
                if (btn.dataset.profile === 'ong') {
                    if (ngoForm) ngoForm.classList.remove('hidden');
                    if (volForm) volForm.classList.add('hidden');
                } else {
                    if (ngoForm) ngoForm.classList.add('hidden');
                    if (volForm) volForm.classList.remove('hidden');
                }
            });
        });
    }
});