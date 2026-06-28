document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const startButton = document.getElementById("start-btn");
  const video = document.getElementById("background-video");
  const soundToggle = document.getElementById("sound-toggle");
  const soundIcon = document.querySelector(".sound-icon");

  // Apparition fluide du texte et du bouton
  window.addEventListener("load", () => {
    document.querySelector(".hero-text").style.opacity = "1";
    document.querySelector(".hero-text").style.transform = "translateY(0)";
    startButton.style.opacity = "1";
    startButton.style.transform = "translateY(0)";
  });

  // Contrôle du son
  if (soundToggle && video && soundIcon) {
    soundToggle.addEventListener("click", () => {
      video.muted = !video.muted;
      soundIcon.textContent = video.muted ? "🔇" : "🔊";
    });
  }

  // Animation et transition lors du clic sur le bouton principal
  if (startButton) {
    startButton.addEventListener("click", () => {
      startButton.disabled = true;

      // Transition visuelle (ex: fondu de la page)
      body.style.transition = "opacity 1s ease-in-out";
      body.style.opacity = "0";

      // Redirection simulée (à adapter si tu as une vraie page)
      setTimeout(() => {
        window.location.href = "histoire.html"; // change ce lien selon ta structure
      }, 1000);
    });
  }
});
