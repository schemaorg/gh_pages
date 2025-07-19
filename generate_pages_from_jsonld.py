#!/usr/bin/env python3
"""
Schema.org page generator from JSON-LD format
"""

import json
import os
import yaml
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

class SchemaJSONLDParser:
    def __init__(self):
        self.types = {}  # type_name -> {label, comment, subclass_of, properties}
        self.properties = {}  # property_name -> {label, comment, domain_includes, range_includes}
        self.inverse_properties = defaultdict(list)  # type -> list of properties that accept this type
        
    def parse_schema_json(self, filename='data/schema.json'):
        """Parse the schema.json file and extract types and properties"""
        print(f"Parsing {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        # Process all items in the graph
        for item in schema_data.get('@graph', []):
            item_id = item.get('@id', '')
            
            # Extract the name from the ID (schema:TypeName -> TypeName)
            if item_id.startswith('schema:'):
                name = item_id[7:]  # Remove 'schema:' prefix
            else:
                continue
            
            item_type = item.get('@type', '')
            
            if item_type == 'rdfs:Class':
                # This is a type/class
                label = item.get('rdfs:label', name)
                comment = item.get('rdfs:comment', '')
                
                # Extract subclass
                subclass_data = item.get('rdfs:subClassOf', {})
                subclass_of = None
                if isinstance(subclass_data, dict) and '@id' in subclass_data:
                    subclass_id = subclass_data['@id']
                    if subclass_id.startswith('schema:'):
                        subclass_of = subclass_id[7:]
                
                self.types[name] = {
                    'label': label,
                    'comment': comment,
                    'subclass_of': subclass_of,
                    'properties': []
                }
                
            elif item_type == 'rdf:Property':
                # This is a property
                label = item.get('rdfs:label', name)
                comment = item.get('rdfs:comment', '')
                
                # Extract domain includes
                domain_includes = []
                domain_data = item.get('schema:domainIncludes', [])
                if not isinstance(domain_data, list):
                    domain_data = [domain_data]
                for domain in domain_data:
                    if isinstance(domain, dict) and '@id' in domain:
                        domain_id = domain['@id']
                        if domain_id.startswith('schema:'):
                            domain_includes.append(domain_id[7:])
                
                # Extract range includes
                range_includes = []
                range_data = item.get('schema:rangeIncludes', [])
                if not isinstance(range_data, list):
                    range_data = [range_data]
                for range_item in range_data:
                    if isinstance(range_item, dict) and '@id' in range_item:
                        range_id = range_item['@id']
                        if range_id.startswith('schema:'):
                            range_includes.append(range_id[7:])
                
                self.properties[name] = {
                    'label': label,
                    'comment': comment,
                    'domain_includes': domain_includes,
                    'range_includes': range_includes
                }
                
                # Build inverse property mapping
                for range_type in range_includes:
                    if range_type in self.types or range_type == 'Text' or range_type == 'URL':
                        self.inverse_properties[range_type].append(name)
        
        # Add properties to types based on domain
        for prop_name, prop_data in self.properties.items():
            for domain_type in prop_data['domain_includes']:
                if domain_type in self.types:
                    self.types[domain_type]['properties'].append(prop_name)
        
        print(f"Parsed {len(self.types)} types and {len(self.properties)} properties")

class JekyllGenerator:
    def __init__(self, schema_parser: SchemaJSONLDParser):
        self.schema_parser = schema_parser
        
    def generate_type_page(self, type_name: str) -> str:
        """Generate Jekyll markdown page for a schema type"""
        type_data = self.schema_parser.types[type_name]
        
        # Prepare front matter
        front_matter = {
            'title': type_name,
            'permalink': f'/{type_name}',
            'type': 'Type',
            'description': type_data['comment'],
            'parent': type_data['subclass_of'] if type_data['subclass_of'] else None,
            'properties': type_data['properties']
        }
        
        # Get inherited properties
        inherited_properties = self.get_inherited_properties(type_name)
        
        # Get subtypes
        subtypes = [t for t, data in self.schema_parser.types.items() 
                   if data['subclass_of'] == type_name]
        
        # Build the content
        content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}---

<div class="type-info">
    <p><strong>{type_data['comment']}</strong></p>
"""
        
        if type_data['subclass_of']:
            content += f"""
    <div class="type-hierarchy">
        <strong>Subclass of:</strong>
        <span class="hierarchy-item"><a href="/{type_data['subclass_of']}">{type_data['subclass_of']}</a></span>
    </div>
"""
        
        if subtypes:
            content += f"""
    <div class="type-hierarchy">
        <strong>More specific types:</strong>
        {', '.join([f'<span class="hierarchy-item"><a href="/{st}">{st}</a></span>' for st in sorted(subtypes)])}
    </div>
"""
        
        content += "</div>\n\n"
        
        # Properties from this type
        if type_data['properties']:
            content += self.generate_properties_table(type_name, sorted(type_data['properties']), f"Properties from {type_name}")
        
        # Inherited properties
        if inherited_properties:
            for parent_type, props in inherited_properties.items():
                if props:
                    content += self.generate_properties_table(parent_type, sorted(props), f"Properties from {parent_type}")
        
        # Properties where this type can be used as a value
        inverse_props = self.schema_parser.inverse_properties.get(type_name, [])
        if inverse_props:
            content += self.generate_inverse_properties_table(sorted(inverse_props), type_name)
        
        return content
    
    def generate_property_page(self, prop_name: str) -> str:
        """Generate Jekyll markdown page for a schema property"""
        prop_data = self.schema_parser.properties[prop_name]
        
        # Prepare front matter
        front_matter = {
            'title': prop_name,
            'permalink': f'/{prop_name}',
            'type': 'Property',
            'description': prop_data['comment'],
            'domain_includes': prop_data['domain_includes'],
            'range_includes': prop_data['range_includes']
        }
        
        content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}---

<div class="type-info">
    <p><strong>{prop_data['comment']}</strong></p>
</div>

<div class="properties-section">
    <h2>Values expected to be one of these types</h2>
    <ul>
"""
        
        for range_type in prop_data['range_includes']:
            if range_type in self.schema_parser.types:
                content += f'        <li><a href="/{range_type}">{range_type}</a></li>\n'
            else:
                content += f'        <li>{range_type}</li>\n'
        
        content += """    </ul>
</div>

<div class="properties-section">
    <h2>Used on these types</h2>
    <ul>
"""
        
        for domain_type in prop_data['domain_includes']:
            content += f'        <li><a href="/{domain_type}">{domain_type}</a></li>\n'
        
        content += """    </ul>
</div>
"""
        
        return content
    
    def generate_properties_table(self, parent_type: str, properties: List[str], title: str) -> str:
        """Generate a properties table section"""
        html = f"""
<div class="properties-section">
    <h2>{title}</h2>
    <table class="property-table">
        <thead>
            <tr>
                <th>Property</th>
                <th>Expected Type</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for prop_name in properties:
            if prop_name in self.schema_parser.properties:
                prop_data = self.schema_parser.properties[prop_name]
                range_types = ', '.join([f'<a href="/{rt}">{rt}</a>' if rt in self.schema_parser.types 
                                       else rt for rt in prop_data['range_includes']])
                html += f"""
            <tr>
                <td><span class="property-name"><a href="/{prop_name}">{prop_name}</a></span></td>
                <td><span class="expected-type">{range_types}</span></td>
                <td>{prop_data['comment']}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</div>
"""
        return html
    
    def generate_inverse_properties_table(self, properties: List[str], type_name: str) -> str:
        """Generate a table of properties that can use this type as a value"""
        html = f"""
<div class="properties-section">
    <h2>Instances of {type_name} may appear as a value for the following properties</h2>
    <table class="property-table">
        <thead>
            <tr>
                <th>Property</th>
                <th>On Types</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for prop_name in properties:
            if prop_name in self.schema_parser.properties:
                prop_data = self.schema_parser.properties[prop_name]
                domain_types = ', '.join([f'<a href="/{dt}" class="type-link">{dt}</a>' 
                                        for dt in prop_data['domain_includes']])
                html += f"""
            <tr>
                <td><span class="property-name"><a href="/{prop_name}">{prop_name}</a></span></td>
                <td>{domain_types}</td>
                <td>{prop_data['comment']}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</div>
"""
        return html
    
    def get_inherited_properties(self, type_name: str) -> dict:
        """Get properties inherited from parent types"""
        inherited = {}
        
        def collect_parent_properties(current_type):
            type_data = self.schema_parser.types.get(current_type)
            if not type_data:
                return
                
            parent = type_data['subclass_of']
            if parent and parent in self.schema_parser.types:
                inherited[parent] = self.schema_parser.types[parent]['properties'].copy()
                collect_parent_properties(parent)
        
        collect_parent_properties(type_name)
        return inherited
    
    def generate_all_pages(self, output_dir='docs'):
        """Generate Jekyll collection files"""
        # Create directories for collections
        types_dir = os.path.join(output_dir, '_types')
        props_dir = os.path.join(output_dir, '_properties')
        os.makedirs(types_dir, exist_ok=True)
        os.makedirs(props_dir, exist_ok=True)
        
        print(f"Generating Jekyll pages for {len(self.schema_parser.types)} types...")
        
        # Generate type pages
        for type_name in self.schema_parser.types:
            content = self.generate_type_page(type_name)
            filename = os.path.join(types_dir, f'{type_name}.md')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Generating Jekyll pages for {len(self.schema_parser.properties)} properties...")
        
        # Generate property pages
        for prop_name in self.schema_parser.properties:
            content = self.generate_property_page(prop_name)
            filename = os.path.join(props_dir, f'{prop_name}.md')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Generated {len(self.schema_parser.types) + len(self.schema_parser.properties)} Jekyll pages")

def generate_index_page(schema_parser: SchemaJSONLDParser, output_dir='docs'):
    """Generate index.html with links to all types and properties"""
    
    types_sorted = sorted(schema_parser.types.keys())
    properties_sorted = sorted(schema_parser.properties.keys())
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Vocabulary</title>
    <link rel="stylesheet" href="{{% raw %}}{{{{ site.baseurl }}}}/schema-org.css{{% endraw %}}">
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
        html += f'                        <li><a href="{{% raw %}}{{{{ site.baseurl }}}}/{type_name}{{% endraw %}}">{type_name}</a></li>\n'
    
    html += f"""                    </ul>
                </div>
                
                <div class="index-section">
                    <h3>Properties ({len(properties_sorted)} total)</h3>
                    <ul class="index-list">
"""
    
    for prop_name in properties_sorted:
        html += f'                        <li><a href="{{% raw %}}{{{{ site.baseurl }}}}/{prop_name}{{% endraw %}}">{prop_name}</a></li>\n'
    
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
    # First, convert TTL to JSON if needed
    if not os.path.exists('data/schema.json'):
        print("schema.json not found. Converting from schema.ttl...")
        import convert_ttl_to_jsonld
        convert_ttl_to_jsonld.main()
    
    # Parse schema JSON
    schema_parser = SchemaJSONLDParser()
    schema_parser.parse_schema_json()
    
    # Generate Jekyll pages
    generator = JekyllGenerator(schema_parser)
    generator.generate_all_pages()
    
    # Generate index page
    generate_index_page(schema_parser)
    
    print("Schema.org page generation from JSON-LD complete!")

if __name__ == "__main__":
    main()