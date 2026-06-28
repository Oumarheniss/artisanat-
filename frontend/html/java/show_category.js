document.addEventListener('DOMContentLoaded', () => {
  const category = window.location.pathname
    .split('/')
    .pop()
    .replace('.html', '');

  const API_URL = `http://127.0.0.1:5000/api/artisanat/${category}`;
  const container = document.querySelector('.container');

  fetch(API_URL)
    .then(res => res.json())
    .then(data => {
      container.innerHTML += `<h2>${data.category}</h2>`;

      data.data.forEach(item => {
        const card = document.createElement('div');
        card.classList.add('artisanat-card');

        const title = document.createElement('h3');
        title.textContent = item.title;

        const content = document.createElement('p');
        content.textContent = item.content;

        card.appendChild(title);
        card.appendChild(content);
        container.appendChild(card);
      });
    })
    .catch(err => {
      console.error('Erreur:', err);
      container.innerHTML += `<p style="color:red">Impossible de charger la catégorie.</p>`;
    });
});
