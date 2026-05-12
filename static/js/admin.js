// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all admin functionality
    initSidebar();
    initDropdowns();
    initTables();
    initSearch();
    initFilters();
});

// Sidebar functionality
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminContainer = document.querySelector('.admin-container');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            adminContainer.classList.toggle('sidebar-collapsed');
        });
    }
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.admin-sidebar');
            const sidebarToggle = document.getElementById('sidebarToggle');
            
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                document.querySelector('.admin-container').classList.remove('sidebar-collapsed');
            }
        }
    });
}

// Dropdown functionality
function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Close all other dropdowns
            document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                if (menu !== this.nextElementSibling) {
                    menu.classList.remove('show');
                }
            }.bind(this));
            
            // Toggle current dropdown
            const dropdown = this.nextElementSibling;
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(dropdown) {
                dropdown.classList.remove('show');
            });
        }
    });
}

// Table functionality
function initTables() {
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(function(table) {
        // Add row hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(255, 215, 0, 0.05)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.addEventListener('click', function() {
                const sortField = this.dataset.sort;
                const tableBody = table.querySelector('tbody');
                const rows = Array.from(tableBody.querySelectorAll('tr'));
                
                rows.sort(function(a, b) {
                    const aValue = a.querySelector(`td[data-${sortField}]`).dataset[sortField];
                    const bValue = b.querySelector(`td[data-${sortField}]`).dataset[sortField];
                    
                    if (aValue < bValue) return -1;
                    if (aValue > bValue) return 1;
                    return 0;
                });
                
                rows.forEach(function(row) {
                    tableBody.appendChild(row);
                });
            });
        });
    });
}

// Search functionality
function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            searchTimeout = setTimeout(function() {
                performSearch(query);
            }, 300);
        });
    });
}

function performSearch(query) {
    const tableRows = document.querySelectorAll('.admin-table tbody tr');
    
    tableRows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(query.toLowerCase());
        
        if (matches) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Update results count
    const visibleRows = document.querySelectorAll('.admin-table tbody tr:not([style*="display: none"])');
    const resultsCount = document.querySelector('.results-count');
    
    if (resultsCount) {
        resultsCount.textContent = `Showing ${visibleRows.length} results`;
    }
}

// Filter functionality
function initFilters() {
    const filterDropdowns = document.querySelectorAll('.filter-dropdown');
    
    filterDropdowns.forEach(function(dropdown) {
        dropdown.addEventListener('change', function() {
            const filterValue = this.value;
            const filterField = this.dataset.filter;
            
            applyFilter(filterField, filterValue);
        });
    });
}

function applyFilter(field, value) {
    const tableRows = document.querySelectorAll('.admin-table tbody tr');
    
    tableRows.forEach(function(row) {
        if (value === '') {
            row.style.display = '';
        } else {
            const cellValue = row.querySelector(`td[data-${field}]`).dataset[field];
            
            if (cellValue === value) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
    
    // Update results count
    const visibleRows = document.querySelectorAll('.admin-table tbody tr:not([style*="display: none"])');
    const resultsCount = document.querySelector('.results-count');
    
    if (resultsCount) {
        resultsCount.textContent = `Showing ${visibleRows.length} results`;
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `admin-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to container
    const container = document.querySelector('.admin-notifications');
    if (container) {
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(function() {
            notification.remove();
        }, 5000);
    }
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    
    return icons[type] || 'info-circle';
}

// AJAX helpers
function ajaxRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => response.json())
        .catch(error => {
            console.error('AJAX Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Export functions to global scope
window.adminUtils = {
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    showNotification: showNotification,
    ajaxRequest: ajaxRequest,
    confirmAction: confirmAction
};
