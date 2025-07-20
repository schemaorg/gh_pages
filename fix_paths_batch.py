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
        return True
    return False

# Process all files
files = [
    '/Users/rvguha/v2/schemaorg/docs/docs/schemas.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/gs.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/howwework.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/releases.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/faq.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/datamodel.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/developers.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/extension.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/meddocs.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/hotels.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/index.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/full.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/about.html'
]

updated_count = 0
for filepath in files:
    print(f"Processing: {filepath}")
    if fix_paths_in_file(filepath):
        updated_count += 1
        print(f"  ✓ Updated")
    else:
        print(f"  - No changes needed")

print(f"\nTotal files updated: {updated_count}/{len(files)}")