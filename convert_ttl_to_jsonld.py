#!/usr/bin/env python3
"""
Convert schema.ttl to schema.json in JSON-LD format
"""

import json
import re
from collections import defaultdict

def parse_ttl_to_jsonld(ttl_file='data/schema.ttl'):
    """Convert Turtle format to JSON-LD"""
    
    # Initialize the JSON-LD structure
    jsonld = {
        "@context": {
            "schema": "https://schema.org/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc": "http://purl.org/dc/terms/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "owl": "http://www.w3.org/2002/07/owl#",
            "void": "http://rdfs.org/ns/void#"
        },
        "@graph": []
    }
    
    with open(ttl_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse types (classes)
    type_pattern = r':(\w+)\s+a\s+rdfs:Class\s*;(.*?)(?=\n:|\n\n|\Z)'
    for match in re.finditer(type_pattern, content, re.DOTALL):
        type_name = match.group(1)
        type_def = match.group(2)
        
        type_obj = {
            "@id": f"schema:{type_name}",
            "@type": "rdfs:Class",
            "rdfs:label": type_name
        }
        
        # Extract comment
        comment_match = re.search(r'rdfs:comment\s+"([^"]+)"', type_def)
        if comment_match:
            type_obj["rdfs:comment"] = comment_match.group(1)
        
        # Extract subclass
        subclass_match = re.search(r'rdfs:subClassOf\s+:(\w+)', type_def)
        if subclass_match:
            type_obj["rdfs:subClassOf"] = {"@id": f"schema:{subclass_match.group(1)}"}
        
        # Extract source
        source_match = re.search(r':source\s+<([^>]+)>', type_def)
        if source_match:
            type_obj["schema:source"] = {"@id": source_match.group(1)}
        
        jsonld["@graph"].append(type_obj)
    
    # Parse properties
    prop_pattern = r':(\w+)\s+a\s+rdf:Property\s*;(.*?)(?=\n:|\n\n|\Z)'
    for match in re.finditer(prop_pattern, content, re.DOTALL):
        prop_name = match.group(1)
        prop_def = match.group(2)
        
        prop_obj = {
            "@id": f"schema:{prop_name}",
            "@type": "rdf:Property",
            "rdfs:label": prop_name
        }
        
        # Extract comment
        comment_match = re.search(r'rdfs:comment\s+"([^"]+)"', prop_def)
        if comment_match:
            prop_obj["rdfs:comment"] = comment_match.group(1)
        
        # Extract domain includes
        domain_includes = []
        domain_matches = re.findall(r':domainIncludes\s+:(\w+)', prop_def)
        for domain in domain_matches:
            domain_includes.append({"@id": f"schema:{domain}"})
        if domain_includes:
            prop_obj["schema:domainIncludes"] = domain_includes
        
        # Extract range includes
        range_includes = []
        range_matches = re.findall(r':rangeIncludes\s+:(\w+)', prop_def)
        for range_type in range_matches:
            range_includes.append({"@id": f"schema:{range_type}"})
        if range_includes:
            prop_obj["schema:rangeIncludes"] = range_includes
        
        # Extract source
        source_match = re.search(r':source\s+<([^>]+)>', prop_def)
        if source_match:
            prop_obj["schema:source"] = {"@id": source_match.group(1)}
        
        jsonld["@graph"].append(prop_obj)
    
    # Parse enumerations
    enum_pattern = r':(\w+)\s+a\s+:(\w+)\s*;(.*?)(?=\n:|\n\n|\Z)'
    for match in re.finditer(enum_pattern, content, re.DOTALL):
        item_name = match.group(1)
        enum_type = match.group(2)
        item_def = match.group(3)
        
        # Skip if it's a Class or Property (already handled)
        if enum_type in ['Class', 'Property'] or 'rdfs:Class' in item_def or 'rdf:Property' in item_def:
            continue
        
        # This is an enumeration value
        enum_obj = {
            "@id": f"schema:{item_name}",
            "@type": f"schema:{enum_type}",
            "rdfs:label": item_name
        }
        
        # Extract comment
        comment_match = re.search(r'rdfs:comment\s+"([^"]+)"', item_def)
        if comment_match:
            enum_obj["rdfs:comment"] = comment_match.group(1)
        
        jsonld["@graph"].append(enum_obj)
    
    return jsonld

def main():
    print("Converting schema.ttl to schema.json...")
    
    # Parse the TTL file
    jsonld_data = parse_ttl_to_jsonld()
    
    # Count items
    types_count = sum(1 for item in jsonld_data["@graph"] if item.get("@type") == "rdfs:Class")
    props_count = sum(1 for item in jsonld_data["@graph"] if item.get("@type") == "rdf:Property")
    other_count = len(jsonld_data["@graph"]) - types_count - props_count
    
    print(f"Converted {types_count} types, {props_count} properties, and {other_count} other items")
    
    # Write to JSON file
    output_file = 'data/schema.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jsonld_data, f, indent=2, ensure_ascii=False)
    
    print(f"Schema written to {output_file}")

if __name__ == "__main__":
    main()