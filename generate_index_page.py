#!/usr/bin/env python3
"""
Generate an index page listing all Schema.org types and properties
"""

import os
from generate_schema_pages import SchemaParser

def generate_index_page(schema_parser, output_dir='docs'):
    """Generate index.html with links to all types and properties"""
    
    types_sorted = sorted(schema_parser.types.keys())
    properties_sorted = sorted(schema_parser.properties.keys())
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Vocabulary</title>
    <link rel="stylesheet" href="schema-org.css">
    <style>
        .index-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin: 20px 0;
        }
        .index-section {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
        }
        .index-list {
            columns: 3;
            column-gap: 20px;
        }
        .index-list li {
            break-inside: avoid;
            margin: 5px 0;
        }
        @media (max-width: 768px) {
            .index-container {
                grid-template-columns: 1fr;
            }
            .index-list {
                columns: 2;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Schema.org Vocabulary</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="main-content">
            <h2>Schema.org Type and Property Reference</h2>
            <p>This is a complete list of all types and properties in the Schema.org vocabulary.</p>
            
            <div class="index-container">
                <div class="index-section">
                    <h3>Types ({len(types_sorted)} total)</h3>
                    <ul class="index-list">
"""
    
    for type_name in types_sorted:
        html += f'                        <li><a href="{type_name}">{type_name}</a></li>\n'
    
    html += """                    </ul>
                </div>
                
                <div class="index-section">
                    <h3>Properties ({len(properties_sorted)} total)</h3>
                    <ul class="index-list">
"""
    
    for prop_name in properties_sorted:
        html += f'                        <li><a href="{prop_name}">{prop_name}</a></li>\n'
    
    html += """                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Write index.html
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated index.html with {len(types_sorted)} types and {len(properties_sorted)} properties")

def main():
    # Parse schema
    schema_parser = SchemaParser()
    schema_parser.parse_schema_ttl()
    
    # Generate index page
    generate_index_page(schema_parser)

if __name__ == "__main__":
    main()