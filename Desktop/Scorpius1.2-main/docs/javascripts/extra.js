// Scorpius Enterprise Platform - Extra JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🛡️ Scorpius Enterprise Platform Documentation Loaded');
    
    // Add enterprise branding to the title
    const title = document.querySelector('.md-header__title');
    if (title && !title.querySelector('.scorpius-logo')) {
        const logo = document.createElement('span');
        logo.className = 'scorpius-logo';
        logo.innerHTML = '🛡️ ';
        title.insertBefore(logo, title.firstChild);
    }
    
    // Enhance code blocks
    document.querySelectorAll('pre code').forEach(function(block) {
        block.style.fontFamily = "'JetBrains Mono', 'Fira Code', Consolas, monospace";
    });
    
    // Add smooth scrolling
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
});
