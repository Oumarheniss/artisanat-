document.addEventListener('DOMContentLoaded', () => {
    // Charger les données des artisans
    loadArtisans();
    
    // Vérifier si un hash (ID artisan) est présent dans l'URL
    if (window.location.hash) {
        const artisanId = window.location.hash.substring(1);
        scrollToArtisan(artisanId);
    }
});

async function loadArtisans() {
    try {
        const response = await fetch('data/artisans.json');
        const artisans = await response.json();
        
        const container = document.querySelector('.artisans-container');
        
        artisans.forEach(artisan => {
            const artisanCard = document.createElement('div');
            artisanCard.className = 'artisan-card';
            artisanCard.id = artisan.id;
            
            artisanCard.innerHTML = `
                <div class="artisan-image">
                    <img src="${artisan.image}" alt="${artisan.name}">
                    <div class="rating">${'★'.repeat(artisan.rating)}${'☆'.repeat(5 - artisan.rating)}</div>
                </div>
                <div class="artisan-info">
                    <h2>${artisan.name}</h2>
                    <span class="specialty">${artisan.specialty} - ${artisan.city}</span>
                    <p>${artisan.bio}</p>
                    <div class="artisan-products">
                        <h3>Ses œuvres</h3>
                        <div class="products-mini-grid" id="products-${artisan.id}">
                            <!-- Produits chargés dynamiquement -->
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(artisanCard);
            loadArtisanProducts(artisan.id, artisan.products);
        });
        
    } catch (error) {
        console.error('Error loading artisans:', error);
    }
}

async function loadArtisanProducts(artisanId, productIds) {
    try {
        // Charger tous les produits
        const response = await fetch('data/products.json');
        const allProducts = await response.json();
        
        // Filtrer les produits de cet artisan
        const artisanProducts = allProducts.filter(
            product => productIds.includes(product.id)
        );
        
        const productsGrid = document.getElementById(`products-${artisanId}`);
        
        artisanProducts.forEach(product => {
            productsGrid.innerHTML += `
                <div class="product-mini-card">
                    <img src="${product.image}" alt="${product.name}">
                    <div>
                        <h4>${product.name}</h4>
                        <span class="price">${product.price} MAD</span>
                    </div>
                </div>
            `;
        });
        
    } catch (error) {
        console.error(`Error loading products for artisan ${artisanId}:`, error);
    }
}

function scrollToArtisan(artisanId) {
    const artisanElement = document.getElementById(artisanId);
    if (artisanElement) {
        artisanElement.scrollIntoView({ behavior: 'smooth' });
        
        // Ajouter un effet visuel
        artisanElement.style.animation = 'highlight 2s';
        setTimeout(() => {
            artisanElement.style.animation = '';
        }, 2000);
    }
}