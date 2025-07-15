#!/usr/bin/env python3
import urllib.request
import os

# Base URL for raw files
base_url = "https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/"

# List of example files
example_files = [
    "examples.txt",
    "issue-1004-examples.txt",
    "issue-1100-examples.txt",
    "sdo-ClaimReview-issue-1061-examples.txt",
    "sdo-airport-examples.txt",
    "sdo-apartment-examples.txt",
    "sdo-automobile-examples.txt",
    "sdo-blogpost-examples.txt",
    "sdo-book-series-examples.txt",
    "sdo-bus-stop-examples.txt",
    "sdo-course-examples.txt",
    "sdo-creativework-examples.txt",
    "sdo-datafeed-examples.txt",
    "sdo-defined-region-examples.txt",
    "sdo-dentist-examples.txt",
    "sdo-digital-document-examples.txt",
    "sdo-drug-examples.txt",
    "sdo-examples-goodrelations.txt",
    "sdo-exhibitionevent-examples.txt",
    "sdo-fibo-examples.txt",
    "sdo-hotels-examples.txt",
    "sdo-howto-examples.txt",
    "sdo-identifier-examples.txt",
    "sdo-invoice-examples.txt",
    "sdo-itemlist-examples.txt",
    "sdo-library-examples.txt",
    "sdo-lrmi-examples.txt",
    "sdo-mainEntity-examples.txt",
    "sdo-map-examples.txt",
    "sdo-menu-examples.txt",
    "sdo-music-examples.txt",
    "sdo-offer-shipping-details-examples.txt",
    "sdo-offeredby-examples.txt",
    "sdo-periodical-examples.txt",
    "sdo-police-station-examples.txt",
    "sdo-property-value-examples.txt",
    "sdo-screeningevent-examples.txt",
    "sdo-service-examples.txt",
    "sdo-single-family-residence-examples.txt",
    "sdo-social-media-examples.txt",
    "sdo-soso-dataset-examples.txt",
    "sdo-sports-examples.txt",
    "sdo-tourism-examples.txt",
    "sdo-userinteraction-examples.txt",
    "sdo-vehicle-examples.txt",
    "sdo-videogame-examples.txt",
    "sdo-visualartwork-examples.txt",
    "sdo-website-examples.txt"
]

# Create examples directory if it doesn't exist
os.makedirs("examples", exist_ok=True)

# Download each file
for filename in example_files:
    url = base_url + filename
    target_path = os.path.join("examples", filename)
    
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"✓ Downloaded {filename}")
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")

print(f"\nTotal files attempted: {len(example_files)}")
print("Download complete!")