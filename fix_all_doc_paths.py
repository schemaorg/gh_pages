#!/usr/bin/env python3
"""
Fix all asset and link paths in docs HTML files
"""

import os
import re

def fix_paths_in_file(filepath):
    """Fix all paths in a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix favicon path
    content = re.sub(r'href="/docs/favicon\.ico"', 'href="../favicon.ico"', content)
    
    # Fix schemaorg.css to schema-org.css and correct path
    content = re.sub(r'href="/docs/schemaorg\.css"', 'href="../schema-org.css"', content)
    
    # Fix CSS files that should stay in docs folder
    content = re.sub(r'href="/docs/(devnote|prettify)\.css"', r'href="\1.css"', content)
    
    # Fix JS files
    content = re.sub(r'src="/docs/(schemaorg|prettify)\.js"', r'src="\1.js"', content)
    
    # Fix links to other HTML pages in docs
    content = re.sub(r'href="/docs/([^"]+\.html)"', r'href="\1"', content)
    
    # Fix image paths
    content = re.sub(r'src="/docs/([^"]+\.(png|jpg|gif))"', r'src="\1"', content)
    
    # Fix any remaining /docs/ paths
    content = re.sub(r'(href|src)="/docs/([^"]+)"', r'\1="\2"', content)
    
    # Save if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    docs_dir = 'docs/docs'
    html_files = []
    
    # Get all HTML files
    for file in os.listdir(docs_dir):
        if file.endswith('.html'):
            html_files.append(os.path.join(docs_dir, file))
    
    print(f"Processing {len(html_files)} HTML files...")
    
    for filepath in html_files:
        filename = os.path.basename(filepath)
        if fix_paths_in_file(filepath):
            print(f"✓ Fixed: {filename}")
        else:
            print(f"  No changes: {filename}")

if __name__ == "__main__":
    main()