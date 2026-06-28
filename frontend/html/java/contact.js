document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Animation des champs du formulaire
    const formInputs = document.querySelectorAll('.form-group input, .form-group textarea');
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (input.value === '') {
                input.parentNode.classList.remove('focused');
            }
        });
    });
});

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Désactiver le bouton pendant l'envoi
    submitBtn.disabled = true;
    submitBtn.textContent = 'Envoi en cours...';
    
    try {
        // Simulation d'envoi (remplacer par un vrai fetch vers votre backend)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Afficher un message de succès
        showMessage('success', 'Message envoyé avec succès ! Nous vous contacterons bientôt.');
        form.reset();
        
    } catch (error) {
        console.error('Error submitting form:', error);
        showMessage('error', 'Une erreur est survenue. Veuillez réessayer.');
        
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Envoyer';
    }
}

function showMessage(type, text) {
    const existingMessage = document.querySelector('.form-message');
    if (existingMessage) existingMessage.remove();
    
    const message = document.createElement('div');
    message.className = `form-message ${type}`;
    message.textContent = text;
    
    const form = document.getElementById('contactForm');
    form.insertBefore(message, form.firstChild);
    
    // Disparaître après 5 secondes
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 500);
    }, 5000);
}