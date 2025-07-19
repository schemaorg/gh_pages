#!/usr/bin/env python3
"""
Download Schema.org documentation pages from their sitemap
"""

import os
import re
import time
import requests
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET

def fetch_sitemap(url):
    """Fetch and parse the sitemap XML"""
    print(f"Fetching sitemap from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_urls_from_sitemap(xml_content):
    """Extract all URLs from the sitemap XML"""
    # Parse the XML
    root = ET.fromstring(xml_content)
    
    # Define the namespace
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    # Find all URL elements
    urls = []
    for url_elem in root.findall('.//ns:url/ns:loc', namespace):
        if url_elem.text:
            urls.append(url_elem.text.strip())
    
    return urls

def filter_docs_urls(urls):
    """Filter URLs that contain '/docs/' in the path"""
    docs_urls = []
    for url in urls:
        if '/docs/' in url:
            docs_urls.append(url)
    return docs_urls

def get_filename_from_url(url):
    """Extract a suitable filename from the URL"""
    # Parse the URL
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove the /docs/ prefix if present
    if path.startswith('/docs/'):
        path = path[6:]
    
    # If path ends with /, add index.html
    if path.endswith('/'):
        path = path + 'index.html'
    
    # If path doesn't have an extension, add .html
    if '.' not in os.path.basename(path):
        path = path + '.html'
    
    # Clean up the path
    path = path.strip('/')
    
    return path

def download_page(url, output_path):
    """Download a page and save it to the specified path"""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  Saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def main():
    # Configuration
    sitemap_url = "https://schema.org/docs/sitemap.xml"
    output_dir = "docs/docs"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch and parse sitemap
    try:
        sitemap_content = fetch_sitemap(sitemap_url)
        all_urls = extract_urls_from_sitemap(sitemap_content)
        print(f"Found {len(all_urls)} total URLs in sitemap")
        
        # Filter for /docs/ URLs
        docs_urls = filter_docs_urls(all_urls)
        print(f"Found {len(docs_urls)} URLs containing '/docs/'")
        
        # Save the list of URLs
        urls_file = os.path.join(output_dir, 'downloaded_urls.txt')
        with open(urls_file, 'w') as f:
            for url in docs_urls:
                f.write(url + '\n')
        print(f"Saved URL list to {urls_file}")
        
        # Download each page
        successful = 0
        failed = 0
        
        for i, url in enumerate(docs_urls, 1):
            print(f"\n[{i}/{len(docs_urls)}] Processing {url}")
            
            # Get filename
            filename = get_filename_from_url(url)
            output_path = os.path.join(output_dir, filename)
            
            # Download the page
            if download_page(url, output_path):
                successful += 1
            else:
                failed += 1
            
            # Be polite to the server
            time.sleep(0.5)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Download complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(docs_urls)}")
        print(f"  Output directory: {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())