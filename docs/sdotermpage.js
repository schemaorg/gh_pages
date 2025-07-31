// Schema.org Term Page JavaScript

$(document).ready(function() {
    // Initialize prettify for code highlighting
    if (typeof prettyPrint === 'function') {
        prettyPrint();
    }
    
    // Handle example tabs
    $('.example-tabs a').click(function(e) {
        e.preventDefault();
        
        var $this = $(this);
        var $tabs = $this.closest('.example-tabs');
        var $content = $tabs.next('.example-content');
        
        // Update active tab
        $tabs.find('a').removeClass('active');
        $this.addClass('active');
        
        // Show corresponding content
        var target = $this.attr('href');
        $content.find('.tab-pane').hide();
        $content.find(target).show();
    });
    
    // Initialize first tab as active
    $('.example-tabs').each(function() {
        $(this).find('a:first').addClass('active');
        $(this).next('.example-content').find('.tab-pane:first').show();
    });
    
    // Add expand/collapse functionality to property sections
    $('.property-section h3').click(function() {
        $(this).next('.property-list').slideToggle();
        $(this).toggleClass('collapsed');
    });
    
    // Copy to clipboard functionality for examples
    $('.copy-button').click(function() {
        var $code = $(this).prev('pre');
        var text = $code.text();
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                // Show feedback
                var $button = $(this);
                var originalText = $button.text();
                $button.text('Copied!');
                setTimeout(function() {
                    $button.text(originalText);
                }, 2000);
            }.bind(this));
        }
    });
    
    // Handle property table row highlighting
    $('.definition-table tr').hover(
        function() {
            $(this).addClass('highlight');
        },
        function() {
            $(this).removeClass('highlight');
        }
    );
    
    // Navigation menu for mobile
    function navFunction() {
        var x = document.getElementById("pagehead1");
        if (x.className === "mobnav") {
            x.className += " responsive";
            document.getElementById("open").style.display = "none";
            document.getElementById("close").style.display = "block";
        } else {
            x.className = "mobnav";
            document.getElementById("open").style.display = "block";
            document.getElementById("close").style.display = "none";
        }
    }
    
    // Make navFunction available globally
    window.navFunction = navFunction;
    
    // Initialize close button as hidden
    $('#close').hide();
    
    // Smooth scroll for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
    
    // Add external link indicators
    $('a[href^="http"]:not([href*="schema.org"])').each(function() {
        $(this).addClass('external');
        $(this).attr('target', '_blank');
        $(this).attr('rel', 'noopener noreferrer');
    });
    
    // Handle property filtering (if search box exists)
    $('#property-filter').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('.property-list li').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Add anchors to headings
    $('h2[id], h3[id]').each(function() {
        var id = $(this).attr('id');
        $(this).append(' <a class="headerlink" href="#' + id + '" title="Permalink to this headline">¶</a>');
    });
    
    // Show headerlinks on hover
    $('h2[id], h3[id]').hover(
        function() {
            $(this).find('.headerlink').css('visibility', 'visible');
        },
        function() {
            $(this).find('.headerlink').css('visibility', 'hidden');
        }
    );
});