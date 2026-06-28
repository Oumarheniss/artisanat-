document.addEventListener('DOMContentLoaded', () => {
  const API_URL = 'http://127.0.0.1:5000/api/artisanat/sources'; // Change si tu veux regrouper par "category" au lieu de "source"
  const buttonsGroup = document.querySelector('.buttons-group');

  fetch(API_URL)
    .then(res => res.json())
    .then(data => {
      const categories = data.sources; // ou `data.categories` si tu fais une route spécifique

      categories.forEach(category => {
        const btn = document.createElement('a');
        btn.href = `${category}.html`; // Ex: "bois.html"
        btn.classList.add('category-btn');
        btn.textContent = `Les arts de ${category}`;

        buttonsGroup.appendChild(btn);
      });
    })
    .catch(err => {
      console.error('Erreur de chargement des catégories:', err);
      buttonsGroup.innerHTML = '<p style="color: red;">Impossible de charger les catégories.</p>';
    });
    
});
