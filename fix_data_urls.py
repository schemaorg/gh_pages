#!/usr/bin/env python3
import os
import glob

# List of HTML files to process
files = [
    '/Users/rvguha/v2/schemaorg/docs/docs/datamodel.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/faq.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/releases.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/developers.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/hotels.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/gs.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/howwework.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/index.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/about.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/full.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/meddocs.html',
    '/Users/rvguha/v2/schemaorg/docs/docs/extension.html'
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace data-resultsUrl="/docs/search_results.html" with data-resultsUrl="search_results.html"
    new_content = content.replace('data-resultsUrl="/docs/search_results.html"', 'data-resultsUrl="search_results.html"')
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated: {os.path.basename(filepath)}")

print("Done!")