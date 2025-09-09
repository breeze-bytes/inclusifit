
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

  const headers = document.querySelectorAll('.accordion-header');

headers.forEach(header => {
header.addEventListener('click', () => {
  const content = header.nextElementSibling;
  const arrow = header.querySelector('.arrow');
  content.classList.toggle('show');
  arrow.style.transform = content.classList.contains('show') ? 'rotate(90deg)' : 'rotate(0deg)';
});
});
