// Add this to your existing main.js or create a new search.js file

// Function to get CSRF token from cookie, meta tag, or hidden input
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
    // If not found in cookie, try meta tag
    if (!cookieValue) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            cookieValue = metaTag.getAttribute('content');
        }
    }
    // If still not found, try hidden input
    if (!cookieValue) {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            cookieValue = csrfInput.value;
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {

    // ===== PRODUCT SEARCH FUNCTIONALITY =====
    const searchForm = document.getElementById('searchForm');
    
    if (searchForm) {
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const searchLoading = document.getElementById('searchLoading');
        
        // Guest mode fields (optional - only if user is not logged in)
        const guestAge = document.getElementById('guestAge');
        const guestAllergies = document.getElementById('guestAllergies');
        const guestHealthConditions = document.getElementById('guestHealthConditions');
        
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const productName = searchInput.value.trim();
            
            if (!productName) {
                alert('Please enter a product name');
                return;
            }
            
            // Show loading immediately
            if (searchLoading) {
                searchLoading.style.display = 'block';
            }
            if (searchBtn) {
                searchBtn.disabled = true;
                searchBtn.textContent = 'Searching...';
            }
            
            try {
                // Prepare request data
                const requestData = {
                    product_name: productName
                };
                
                // Add guest mode data if fields exist
                if (guestAge && guestAge.value) {
                    requestData.age = parseInt(guestAge.value);
                }
                if (guestAllergies && guestAllergies.value) {
                    requestData.allergies = guestAllergies.value;
                }
                if (guestHealthConditions && guestHealthConditions.value) {
                    requestData.health_conditions = guestHealthConditions.value;
                }
                
                // Add timeout to prevent hanging
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
                
                const response = await fetch('/api/search/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                const data = await response.json();
                
                console.log('Search response:', response.status, data);
                
                // Check if multiple products found (brand-only search)
                if (data.multiple_products) {
                    // Redirect to products page instead of showing overlay
                    const params = new URLSearchParams({
                        search: data.search_term,
                        products: JSON.stringify(data.products),
                        age: data.user_data.age || '',
                        allergies: data.user_data.allergies || '',
                        health_conditions: data.user_data.health_conditions || ''
                    });
                    window.location.href = `/products/?${params.toString()}`;
                    return;
                }
                
                if (data.error) {
                    // Show error with suggestions
                    let errorMsg = data.error;
                    if (data.suggestions) {
                        errorMsg += '\n\nTry:\n• ' + data.suggestions.join('\n• ');
                    }
                    alert(errorMsg);
                    if (searchLoading) searchLoading.style.display = 'none';
                    if (searchBtn) {
                        searchBtn.disabled = false;
                        searchBtn.textContent = 'Search Product';
                    }
                    return;
                }
                
                if (data.scan_id) {
                    // Redirect to results page
                    window.location.href = `/results/${data.scan_id}/`;
                } else {
                    // Handle unexpected response
                    console.error('Unexpected response format:', data);
                    let errorDetails = `NEW JAVASCRIPT LOADED - Unexpected server response. Status: ${response.status}`;
                    if (data.success === false) {
                        errorDetails += `\nServer says: ${data.error || 'Unknown error'}`;
                    } else {
                        errorDetails += `\nResponse keys: ${Object.keys(data).join(', ')}`;
                    }
                    alert(`Error: ${errorDetails}`);
                    if (searchLoading) searchLoading.style.display = 'none';
                    if (searchBtn) {
                        searchBtn.disabled = false;
                        searchBtn.textContent = 'Search Product';
                    }
                }
                
            } catch (error) {
                console.error('Search error:', error);
                alert('An error occurred while searching. Please try again.');
                if (searchLoading) searchLoading.style.display = 'none';
                if (searchBtn) {
                    searchBtn.disabled = false;
                    searchBtn.textContent = 'Search Product';
                }
            }
        });
    }
    
    
    // ===== PRODUCT SELECTION PAGE =====
    function showProductSelection(products, searchTerm, userData) {
        // Hide search section
        const uploadSection = document.querySelector('.upload-section');
        const searchSection = document.querySelector('.search-section');
        
        if (uploadSection) uploadSection.style.display = 'none';
        if (searchSection) searchSection.style.display = 'none';
        
        // Create product selection container
        const container = document.createElement('div');
        container.className = 'product-selection-container';
        container.style.cssText = `
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        `;
        
        // Header with back button
        const header = document.createElement('div');
        header.style.cssText = `
            margin-bottom: 2rem;
        `;
        header.innerHTML = `
            <button onclick="window.location.reload()" class="btn-secondary" style="margin-bottom: 1rem;">
                ← Back to Search
            </button>
            <h2 style="font-size: 1.75rem; margin-bottom: 0.5rem;">
                Select a Product from "${searchTerm}"
            </h2>
            <p style="color: #666;">Found ${products.length} product${products.length > 1 ? 's' : ''}</p>
        `;
        
        // Product list
        const productList = document.createElement('div');
        productList.className = 'product-list';
        productList.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 1rem;
        `;
        
        products.forEach((product, index) => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.style.cssText = `
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            `;
            
            productCard.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem; color: black;">
                            ${product.product_name}
                        </h3>
                        <p style="color: #666; margin-bottom: 0.5rem;">
                            <strong>Brand:</strong> ${product.brand}
                        </p>
                        <p style="color: #666; font-size: 0.9rem;">
                            <strong>Source:</strong> ${product.source}
                        </p>
                        ${product.ingredients_text ? 
                            `<p style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">
                                Ingredients available ✓
                            </p>` : ''}
                    </div>
                    <button class="btn-primary" style="margin-left: 1rem;">
                        Analyze This Product
                    </button>
                </div>
            `;
            
            // Hover effects
            productCard.addEventListener('mouseenter', () => {
                productCard.style.transform = 'translateY(-2px)';
                productCard.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            });
            
            productCard.addEventListener('mouseleave', () => {
                productCard.style.transform = 'translateY(0)';
                productCard.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            });
            
            // Click to analyze
            productCard.addEventListener('click', () => {
                analyzeSelectedProduct(product, userData);
            });
            
            productList.appendChild(productCard);
        });
        
        container.appendChild(header);
        container.appendChild(productList);
        
        // Insert into page
        const mainContainer = document.querySelector('.container') || document.querySelector('main');
        if (mainContainer) {
            mainContainer.appendChild(container);
        }
    }
    
    
    // ===== ANALYZE SELECTED PRODUCT =====
    async function analyzeSelectedProduct(product, userData) {
        // Show loading
        const loadingDiv = document.createElement('div');
        loadingDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            z-index: 9999;
        `;
        loadingDiv.innerHTML = `
            <div style="text-align: center;">
                <div class="loading-spinner" style="margin-bottom: 1rem;"></div>
                <p style="color: black;">Analyzing ${product.product_name}...</p>
            </div>
        `;
        document.body.appendChild(loadingDiv);
        
        try {
            // Add timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            const response = await fetch('/api/analyze-product/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product: product,
                    user_data: userData
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            document.body.removeChild(loadingDiv);
            
            console.log('Analyze product response:', response.status, data);
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            if (data.scan_id) {
                window.location.href = `/results/${data.scan_id}/`;
            }
            
        } catch (error) {
            document.body.removeChild(loadingDiv);
            console.error('Analysis error:', error);
            alert('An error occurred while analyzing. Please try again.');
        }
    }
    
    
    // ===== HISTORY MANAGEMENT (for logged-in users) =====
    const deleteHistoryButtons = document.querySelectorAll('.delete-history-btn');
    
    deleteHistoryButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            
            const historyId = button.dataset.historyId;
            
            if (!confirm('Are you sure you want to delete this item?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/history/delete/${historyId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Remove the item from DOM
                    button.closest('.history-item').remove();
                } else {
                    alert('Error deleting item: ' + (data.error || 'Unknown error'));
                }
                
            } catch (error) {
                console.error('Delete error:', error);
                alert('An error occurred while deleting.');
            }
        });
    });
    
    const clearAllHistoryBtn = document.getElementById('clearAllHistoryBtn');
    
    if (clearAllHistoryBtn) {
        clearAllHistoryBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/history/clear/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Reload the page to show empty history
                    window.location.reload();
                } else {
                    alert('Error clearing history: ' + (data.error || 'Unknown error'));
                }
                
            } catch (error) {
                console.error('Clear history error:', error);
                alert('An error occurred while clearing history.');
            }
        });
    }
});