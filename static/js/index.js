// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
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

// Accordion toggle
const headers = document.querySelectorAll('.accordion-header');

headers.forEach(header => {
  header.addEventListener('click', () => {
    const content = header.nextElementSibling;
    const arrow = header.querySelector('.arrow');
    content.classList.toggle('show');
    arrow.style.transform = content.classList.contains('show')
      ? 'rotate(90deg)'
      : 'rotate(0deg)';
  });
});

// Auto-hide Django messages after 5 seconds
document.addEventListener("DOMContentLoaded", function() {
  setTimeout(() => {
    const messages = document.querySelectorAll("#django-messages .alert");
    messages.forEach(msg => {
      msg.style.transition = "opacity 0.5s ease";
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 500); // remove after fade
    });
  }, 5000); // 5 seconds
});
