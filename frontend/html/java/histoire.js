// histoire.js

document.addEventListener('DOMContentLoaded', function() {
  // ========== VARIABLES GLOBALES ==========
  const header = document.querySelector('header');
  const timelineButtons = document.querySelectorAll('.period-btn');
  const contentSections = document.querySelectorAll('.content');
  const video = document.getElementById('background-video');
  const videoFallback = document.querySelector('.video-fallback');
  const navLinks = document.querySelectorAll('.nav-link');
  
  // ========== GESTION DU HEADER ==========
  // Effet de réduction au scroll
  window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  // ========== TIMELINE INTERACTIVE ==========
  timelineButtons.forEach(button => {
    button.addEventListener('click', function() {
      const targetId = this.getAttribute('aria-controls');
      
      // Mise à jour des boutons
      timelineButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
      });
      
      this.classList.add('active');
      this.setAttribute('aria-selected', 'true');
      
      // Mise à jour des sections de contenu
      contentSections.forEach(section => {
        section.hidden = true;
        section.classList.remove('active');
      });
      
      const targetSection = document.getElementById(targetId);
      targetSection.hidden = false;
      targetSection.classList.add('active');
      
      // Animation de scroll doux vers la section
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // ========== GESTION DE LA VIDEO ==========
  // Fallback si la vidéo ne charge pas
  video.addEventListener('error', function() {
    video.style.display = 'none';
    if (videoFallback) {
      videoFallback.style.display = 'block';
    }
  });

  // Tentative de lecture automatique pour certains navigateurs mobiles
  function attemptAutoPlay() {
    const promise = video.play();
    
    if (promise !== undefined) {
      promise.catch(error => {
        // Fallback silencieux si autoplay est bloqué
        video.muted = true;
        video.play();
      });
    }
  }
  
  // Détection de la connexion pour optimiser le chargement
  if (navigator.connection) {
    if (navigator.connection.effectiveType === 'slow-2g' || 
        navigator.connection.saveData === true) {
      video.removeAttribute('autoplay');
    } else {
      attemptAutoPlay();
    }
  }

  // ========== NAVIGATION ACCESSIBLE ==========
  // Navigation au clavier pour la timeline
  timelineButtons.forEach((button, index) => {
    button.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.click();
      }
      
      // Navigation par flèches
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = (index + 1) % timelineButtons.length;
        timelineButtons[nextIndex].focus();
      }
      
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = (index - 1 + timelineButtons.length) % timelineButtons.length;
        timelineButtons[prevIndex].focus();
      }
    });
  });

  // ========== ANIMATIONS ==========
  // Intersection Observer pour les animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = 1;
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Application de l'observer aux éléments
  document.querySelectorAll('.content, .period-btn').forEach(el => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // ========== GESTION DES LIENS ACTIFS ==========
  navLinks.forEach(link => {
    if (link.href === window.location.href) {
      link.setAttribute('aria-current', 'page');
      link.classList.add('active');
    }
  });

  // ========== OPTIMISATION DES PERFORMANCES ==========
  // Délai du chargement de la police
  setTimeout(() => {
    document.body.style.fontFamily = "'Amiri', serif";
  }, 1000);

  // Préchargement des images des autres pages
  if (window.requestIdleCallback) {
    window.requestIdleCallback(() => {
      ['index', 'categories'].forEach(page => {
        const img = new Image();
        img.src = `images/${page}-preload.jpg`;
      });
    });
  }
});

// ========== POLYFILLS ==========
// Polyfill pour forEach sur NodeList pour les vieux navigateurs
if (window.NodeList && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = Array.prototype.forEach;
}