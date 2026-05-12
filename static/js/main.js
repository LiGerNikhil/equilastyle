// EQUILA Fashion - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavbar();
    initScrollEffects();
    initAnimations();
    initTooltips();
    initModals();
    initForms();
    initCart();
    initLazyLoading();
});

// Navbar scroll effect
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.padding = '0.5rem 0';
            navbar.style.boxShadow = '0 5px 30px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.padding = '1rem 0';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        }
    });
}

// Scroll effects
function initScrollEffects() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

// Animations
function initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.card, .product-card, .category-card').forEach(el => {
        observer.observe(el);
    });
    
    // Hover effects for cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Tooltips
function initTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Modals
function initModals() {
    // Quick view modal for products
    document.querySelectorAll('.quick-view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            // Load product details via AJAX
            loadProductDetails(productId);
        });
    });
}

// Forms
function initForms() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    });
}

// Shopping cart functionality
function initCart() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const quantity = this.dataset.quantity || 1;
            addToCart(productId, quantity);
        });
    });
    
    // Quantity selectors
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        const input = selector.querySelector('input');
        const minusBtn = selector.querySelector('.minus-btn');
        const plusBtn = selector.querySelector('.plus-btn');
        
        if (minusBtn) {
            minusBtn.addEventListener('click', function() {
                const currentVal = parseInt(input.value) || 1;
                if (currentVal > 1) {
                    input.value = currentVal - 1;
                    updateCartItem(input.dataset.itemId, input.value);
                }
            });
        }
        
        if (plusBtn) {
            plusBtn.addEventListener('click', function() {
                const currentVal = parseInt(input.value) || 1;
                input.value = currentVal + 1;
                updateCartItem(input.dataset.itemId, input.value);
            });
        }
        
        if (input) {
            input.addEventListener('change', function() {
                updateCartItem(this.dataset.itemId, this.value);
            });
        }
    });
}

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Utility functions
function showToast(message, type = 'success') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    toastContainer.appendChild(toastElement.firstElementChild);
    
    const toast = new bootstrap.Toast(toastContainer.lastElementChild);
    toast.show();
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    const strengthIndicator = document.getElementById('password-strength');
    if (strengthIndicator) {
        strengthIndicator.className = `strength-${strength}`;
        const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][strength];
        strengthIndicator.textContent = strengthText;
    }
}

function addToCart(productId, quantity) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Product added to cart successfully!');
            updateCartUI(data.cart);
        } else {
            showToast(data.message || 'Error adding product to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error adding product to cart', 'error');
    });
}

function updateCartItem(itemId, quantity) {
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartUI(data.cart);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateCartUI(cartData) {
    // Update cart count in navigation
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(el => {
        el.textContent = cartData.total_items;
    });
    
    // Update cart total if on cart page
    const cartTotalElement = document.getElementById('cart-total');
    if (cartTotalElement) {
        cartTotalElement.textContent = `$${cartData.total_price}`;
    }
}

function loadProductDetails(productId) {
    fetch(`/products/api/${productId}/`)
        .then(response => response.json())
        .then(data => {
            // Populate modal with product details
            const modal = document.getElementById('quickViewModal');
            if (modal) {
                modal.querySelector('.modal-title').textContent = data.name;
                modal.querySelector('.modal-body img').src = data.image;
                modal.querySelector('.product-description').textContent = data.description;
                modal.querySelector('.product-price').textContent = `$${data.price}`;
                
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        })
        .catch(error => {
            console.error('Error:', error);
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

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

function performSearch(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-muted">No products found</div>';
    } else {
        const resultsHtml = results.map(product => `
            <a href="/products/product/${product.slug}/" class="d-flex align-items-center p-3 text-decoration-none border-bottom">
                <img src="${product.image}" alt="${product.name}" class="me-3" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
                <div>
                    <div class="fw-semibold">${product.name}</div>
                    <div class="text-muted small">$${product.price}</div>
                </div>
            </a>
        `).join('');
        
        searchResults.innerHTML = resultsHtml;
    }
    
    searchResults.style.display = 'block';
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', initSearch);
