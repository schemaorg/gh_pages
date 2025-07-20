#!/usr/bin/env python3
import os
import re
import glob

def fix_paths_in_file(filepath):
    """Fix absolute paths to relative paths in an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace favicon.ico
    content = re.sub(r'href="/docs/favicon\.ico"', 'href="../favicon.ico"', content)
    
    # Replace schemaorg.css with schema-org.css (note the different filename)
    content = re.sub(r'href="/docs/schemaorg\.css"', 'href="../schema-org.css"', content)
    
    # Replace other CSS files in /docs/ with relative paths
    content = re.sub(r'href="/docs/([^/]+\.css)"', r'href="\1"', content)
    
    # Replace JS files in /docs/ with relative paths
    content = re.sub(r'src="/docs/([^/]+\.js)"', r'src="\1"', content)
    
    # Replace HTML links in /docs/ with relative paths
    content = re.sub(r'href="/docs/([^/]+\.html)"', r'href="\1"', content)
    
    # Replace any remaining /docs/ paths with relative paths
    # This catches paths like /docs/detailTree/detailTree.css
    content = re.sub(r'(href|src)="/docs/([^"]+)"', r'\1="\2"', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")
        return True
    else:
        print(f"No changes needed: {filepath}")
        return False

def main():
    # Get all HTML files in docs/docs/
    html_files = glob.glob('docs/docs/*.html')
    
    if not html_files:
        print("No HTML files found in docs/docs/")
        return
    
    print(f"Found {len(html_files)} HTML files to process")
    updated_count = 0
    
    for filepath in html_files:
        if fix_paths_in_file(filepath):
            updated_count += 1
    
    print(f"\nSummary: Updated {updated_count} out of {len(html_files)} files")

if __name__ == "__main__":
    main()