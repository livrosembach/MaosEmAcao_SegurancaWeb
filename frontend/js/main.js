document.addEventListener('DOMContentLoaded', () => {
  // Mobile Menu Toggle
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  
  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (window.innerWidth < 768 && sidebar && sidebar.classList.contains('open')) {
      if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    }
  });

  // Modal Functionality
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modalCloses = document.querySelectorAll('[data-modal-close]');
  
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const targetId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(targetId);
      if (modal) modal.classList.add('open');
    });
  });

  modalCloses.forEach(close => {
    close.addEventListener('click', () => {
      const modal = close.closest('.modal-backdrop');
      if (modal) modal.classList.remove('open');
    });
  });

  // Highlight active sidebar item
  const currentPath = window.location.pathname.split('/').pop();
  const sidebarItems = document.querySelectorAll('.sidebar-item');
  
  sidebarItems.forEach(item => {
    const href = item.getAttribute('href');
    if (href && (href === currentPath || (currentPath === '' && href === 'home.html'))) {
      item.classList.add('active');
    }
  });
});

// Utility to create HTML elements safely
function createElement(tag, className, content) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (content) el.innerHTML = content;
  return el;
}
