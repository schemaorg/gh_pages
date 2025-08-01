// Pretty markup layout JavaScript for schema.org examples
(function() {
    'use strict';
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Find all example code blocks
        var examples = document.querySelectorAll('.example pre');
        
        examples.forEach(function(example) {
            // Add prettyprint class if not present
            if (!example.classList.contains('prettyprint')) {
                example.classList.add('prettyprint');
            }
            
            // Wrap in example wrapper if not already wrapped
            if (!example.parentElement.classList.contains('example-wrapper')) {
                var wrapper = document.createElement('div');
                wrapper.className = 'example-wrapper';
                example.parentNode.insertBefore(wrapper, example);
                wrapper.appendChild(example);
            }
        });
        
        // Initialize syntax highlighting if prettyPrint is available
        if (typeof prettyPrint === 'function') {
            prettyPrint();
        }
    });
    
    // Handle tab switching for examples with multiple formats
    window.switchExampleTab = function(tabId, contentId) {
        // Hide all tab contents in the same container
        var container = document.getElementById(contentId).parentElement;
        var contents = container.querySelectorAll('.example-tab-content');
        contents.forEach(function(content) {
            content.style.display = 'none';
        });
        
        // Show selected content
        document.getElementById(contentId).style.display = 'block';
        
        // Update active tab
        var tabs = container.querySelectorAll('.example-tab');
        tabs.forEach(function(tab) {
            tab.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
    };
})();