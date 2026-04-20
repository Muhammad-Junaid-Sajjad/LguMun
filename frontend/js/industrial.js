/* Industrial JavaScript - Core Functionality */
/* Validation, Loading States, Error Handling, Keyboard Shortcuts */

// ============================================
// 1. LOADING STATE MANAGEMENT
// ============================================

function showLoading(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.innerHTML = '<div class="skeleton" style="height: 200px; width: 100%;"></div>';
}

function hideLoading(elementId, content) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.innerHTML = content;
}

function showLoadingOverlay(message = 'Loading...') {
  const overlay = document.createElement('div');
  overlay.id = 'loading-overlay';
  overlay.className = 'loading-overlay';
  overlay.innerHTML = `
    <div class="spinner"></div>
    <p>${message}</p>
  `;
  document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.remove();
  }
}

// ============================================
// 2. ERROR HANDLING
// ============================================

function showError(message, recoveryAction = null) {
  const banner = document.createElement('div');
  banner.className = 'error-banner';
  banner.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="8" x2="12" y2="12"></line>
      <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>
    <div style="flex: 1;">
      <h4>Error</h4>
      <p>${message}</p>
      ${recoveryAction ? `<button class="btn-secondary" style="margin-top: 0.5rem;" onclick="${recoveryAction}">Try Again</button>` : ''}
    </div>
    <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--error);">&times;</button>
  `;

  // Insert at top of main content or body
  const main = document.querySelector('main') || document.body;
  main.insertBefore(banner, main.firstChild);

  // Auto-dismiss after 10 seconds if no recovery action
  if (!recoveryAction) {
    setTimeout(() => banner.remove(), 10000);
  }
}

function showSuccess(message) {
  const banner = document.createElement('div');
  banner.className = 'alert-warning';
  banner.style.background = '#d1fae5';
  banner.style.borderColor = '#a7f3d0';
  banner.style.borderLeftColor = 'var(--success)';
  banner.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
    <p>${message}</p>
    <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; margin-left: auto;">&times;</button>
  `;

  const main = document.querySelector('main') || document.body;
  main.insertBefore(banner, main.firstChild);

  setTimeout(() => banner.remove(), 5000);
}

// ============================================
// 3. FORM VALIDATION
// ============================================

function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function isValidPhone(phone) {
  const regex = /^[\d\s\-\+\(\)]+$/;
  return regex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

function validateField(input) {
  const value = input.value.trim();
  const type = input.type;
  const name = input.name;

  let isValid = true;
  let message = '';

  // Required field check
  if (input.required && !value) {
    isValid = false;
    message = 'This field is required';
  }
  // Email validation
  else if (type === 'email' && value && !isValidEmail(value)) {
    isValid = false;
    message = 'Please enter a valid email address';
  }
  // Phone validation
  else if (name === 'phone' && value && !isValidPhone(value)) {
    isValid = false;
    message = 'Please enter a valid phone number';
  }
  // Min length check
  else if (input.minLength && value.length < input.minLength) {
    isValid = false;
    message = `Minimum ${input.minLength} characters required`;
  }

  updateFieldState(input, isValid, message);
  return isValid;
}

function updateFieldState(input, isValid, message) {
  const wrapper = input.closest('.form-field');
  if (!wrapper) return;

  const errorEl = wrapper.querySelector('.form-error');

  if (isValid) {
    input.classList.remove('error');
    input.classList.add('success');
    if (errorEl) {
      errorEl.classList.add('hidden');
      errorEl.textContent = '';
    }
  } else {
    input.classList.add('error');
    input.classList.remove('success');
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
    }
  }
}

function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return false;

  const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
  let allValid = true;

  inputs.forEach(input => {
    if (!validateField(input)) {
      allValid = false;
    }
  });

  return allValid;
}

// ============================================
// 4. KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + K for search
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
      searchInput.focus();
    }
  }

  // Escape to close modals/overlays
  if (e.key === 'Escape') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.remove();
    }

    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => modal.remove());
  }
});

// ============================================
// 5. CONFIRMATION DIALOGS
// ============================================

function confirmAction(message, onConfirm, onCancel = null) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  `;

  modal.innerHTML = `
    <div class="modal-content" style="background: white; padding: 2rem; border-radius: 1rem; max-width: 400px; width: 90%;">
      <h3 style="margin-bottom: 1rem;">Confirm Action</h3>
      <p style="margin-bottom: 1.5rem; color: var(--text-secondary);">${message}</p>
      <div style="display: flex; gap: 1rem; justify-content: flex-end;">
        <button class="btn-secondary" onclick="window.modalCancel()">Cancel</button>
        <button class="btn-primary" onclick="window.modalConfirm()">Confirm</button>
      </div>
    </div>
  `;

  window.modalConfirm = () => {
    onConfirm();
    modal.remove();
    delete window.modalConfirm;
    delete window.modalCancel;
  };

  window.modalCancel = () => {
    if (onCancel) onCancel();
    modal.remove();
    delete window.modalConfirm;
    delete window.modalCancel;
  };

  document.body.appendChild(modal);
}

// ============================================
// 6. EXPORT FUNCTIONALITY
// ============================================

function exportToCSV(data, filename) {
  const csv = convertToCSV(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function convertToCSV(data) {
  if (!data || data.length === 0) return '';

  const headers = Object.keys(data[0]);
  const csvRows = [];

  // Add headers
  csvRows.push(headers.join(','));

  // Add data rows
  data.forEach(row => {
    const values = headers.map(header => {
      const value = row[header];
      return `"${String(value).replace(/"/g, '""')}"`;
    });
    csvRows.push(values.join(','));
  });

  return csvRows.join('\n');
}

function exportToPDF() {
  // Simple print-based PDF export
  window.print();
}

function addToCalendar() {
  // Create ICS file for calendar
  const event = {
    title: 'LGU Inter-University MUN 2026',
    start: '2026-06-15T08:00:00',
    end: '2026-06-17T18:00:00',
    location: 'Lahore Garrison University',
    description: 'Inter-University Model United Nations Conference'
  };

  const ics = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:${event.start.replace(/[-:]/g, '')}
DTEND:${event.end.replace(/[-:]/g, '')}
SUMMARY:${event.title}
LOCATION:${event.location}
DESCRIPTION:${event.description}
END:VEVENT
END:VCALENDAR`;

  const blob = new Blob([ics], { type: 'text/calendar' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'lgu-mun-2026.ics';
  link.click();
  URL.revokeObjectURL(url);
}

// ============================================
// 7. DEBOUNCE UTILITY
// ============================================

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================
// 8. LOCAL STORAGE HELPERS
// ============================================

function saveToLocalStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    console.error('Failed to save to localStorage:', e);
    return false;
  }
}

function loadFromLocalStorage(key) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (e) {
    console.error('Failed to load from localStorage:', e);
    return null;
  }
}

// ============================================
// 9. API HELPERS
// ============================================

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

// ============================================
// 10. INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // Add validation to all form inputs
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    input.addEventListener('blur', () => validateField(input));
  });

  // Add active class to current nav link
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.navbar-simple nav a');
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (currentPath === '/' && link.getAttribute('href') === '/')) {
      link.classList.add('active');
    }
  });

  // Mobile menu toggle
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mainNav = document.getElementById('main-nav');

  if (mobileMenuToggle && mainNav) {
    mobileMenuToggle.addEventListener('click', () => {
      mainNav.classList.toggle('active');

      // Update ARIA attribute
      const isExpanded = mainNav.classList.contains('active');
      mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenuToggle.contains(e.target) && !mainNav.contains(e.target)) {
        mainNav.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close menu when link is clicked
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  console.log('Industrial JS initialized');
});
