// Schema.org JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add any required JavaScript functionality here
    console.log('Schema.org docs loaded');
    
    // Handle navigation
    var navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(function(link) {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });
});