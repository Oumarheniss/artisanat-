const apiUrl = 'http://127.0.0.1:5000/api/artisanat';  // Endpoint de l'API

function slugify(text) {
  return text.toString().toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') 
    .replace(/\s+/g, '-')          
    .replace(/[^\w\-]+/g, '')      
    .replace(/\-\-+/g, '-')        
    .replace(/^-+/, '')            
    .replace(/-+$/, '');           
}

fetch(apiUrl)
  .then(res => res.json())
  .then(data => {
    if (data.status !== 'success') {
      throw new Error('Erreur API');
    }

    const allData = data.data;

    // Crée un objet { catégorie: Set(titres) }
    const categoriesMap = {};

    allData.forEach(item => {
      const cat = item.category || 'Autres';
      if (cat.toLowerCase() === 'histoire') return; // Exclure la catégorie "historique"

      const title = item.title || 'Sans titre';

      if (!categoriesMap[cat]) {
        categoriesMap[cat] = new Set();
      }
      categoriesMap[cat].add(title);
    });

    const container = document.getElementById('buttons-group');
    container.innerHTML = '';

    for (const [category, titlesSet] of Object.entries(categoriesMap)) {
      const catTitle = document.createElement('h2');
      catTitle.textContent = category;
      catTitle.style.color = '#f8c471';
      catTitle.style.marginTop = '2rem';
      container.appendChild(catTitle);

      const titlesDiv = document.createElement('div');
      titlesDiv.style.display = 'flex';
      titlesDiv.style.flexWrap = 'wrap';
      titlesDiv.style.gap = '10px';

      titlesSet.forEach(title => {
        const btn = document.createElement('a');
        btn.textContent = title;
        btn.href = 'generated_pages/' + slugify(title) + '.html';
        btn.classList.add('category-btn');
        titlesDiv.appendChild(btn);
      });

      container.appendChild(titlesDiv);
    }
  })
  .catch(err => {
    console.error(err);
    document.getElementById('buttons-group').innerHTML = '<p>Erreur lors du chargement des données.</p>';
  });
