// Detail Tree JavaScript
(function() {
    'use strict';
    
    function initDetailTree() {
        var expandButtons = document.querySelectorAll('.tree-expand');
        
        expandButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                this.classList.toggle('expanded');
                var nextElement = this.nextElementSibling;
                if (nextElement && nextElement.classList.contains('tree-node')) {
                    nextElement.style.display = nextElement.style.display === 'none' ? 'block' : 'none';
                }
            });
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDetailTree);
    } else {
        initDetailTree();
    }
})();