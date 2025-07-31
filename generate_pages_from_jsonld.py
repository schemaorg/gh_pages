#!/usr/bin/env python3
"""
Schema.org page generator from JSON-LD format
"""

import json
import os
import yaml
import re
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
        
        print(f"Loaded JSON with keys: {list(schema_data.keys())}")
        graph = schema_data.get('@graph', [])
        print(f"Found {len(graph)} items in @graph")
        
        # Process all items in the graph
        for idx, item in enumerate(graph):
            item_id = item.get('@id', '')
            
            # Extract the name from the ID (schema:TypeName -> TypeName)
            if item_id.startswith('schema:'):
                name = item_id[7:]  # Remove 'schema:' prefix
            else:
                continue
            
            item_type = item.get('@type', '')
            
            if idx < 5:
                print(f"  Item {idx}: @id={item_id}, @type={item_type}")
            
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
        
    def convert_markdown_links(self, text: str) -> str:
        """Convert [[Term]] style and standard markdown links to HTML links"""
        if not text:
            return text
            
        # Handle language-specific comments (from JSON-LD @value format)
        if isinstance(text, dict) and '@value' in text:
            text = text['@value']
            
        # Convert [[Term]] to <a href="/Term" class="localLink">Term</a>
        pattern = r'\[\[([^\]]+)\]\]'
        
        def replace_schema_link(match):
            term = match.group(1)
            return f'<a href="/{{ site.baseurl }}/{term}" class="localLink">{term}</a>'
        
        converted = re.sub(pattern, replace_schema_link, str(text))
        
        # Convert standard markdown links [text](url) to <a href="url">text</a>
        # This is needed because the content is inside HTML tags where Jekyll won't process markdown
        md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_md_link(match):
            link_text = match.group(1)
            url = match.group(2)
            return f'<a href="{url}">{link_text}</a>'
        
        converted = re.sub(md_link_pattern, replace_md_link, converted)
        
        # Escape any remaining curly braces for Jekyll
        converted = converted.replace('{', '{{').replace('}', '}}')
        
        # But fix the site.baseurl references
        converted = converted.replace('{{{{ site.baseurl }}}}', '{{ site.baseurl }}')
        
        return converted
        
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
        
        # Convert markdown in comment
        converted_comment = self.convert_markdown_links(type_data['comment'])
        
        # Get inherited properties
        inherited_properties = self.get_inherited_properties(type_name)
        
        # Get subtypes
        subtypes = [t for t, data in self.schema_parser.types.items() 
                   if data['subclass_of'] == type_name]
        
        # Build the content
        content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}---

<h1>{type_name}</h1>

<div class="type-info">
    <p>{converted_comment}</p>
"""
        
        if type_data['subclass_of']:
            content += f"""
    <div class="type-hierarchy">
        <strong>Subclass of:</strong>
        <span class="hierarchy-item"><a href="{{{{ site.baseurl }}}}/{type_data['subclass_of']}">{type_data['subclass_of']}</a></span>
    </div>
"""
        
        if subtypes:
            content += f"""
    <div class="type-hierarchy">
        <strong>More specific types:</strong>
        {', '.join([f'<span class="hierarchy-item"><a href="{{{{ site.baseurl }}}}/{st}">{st}</a></span>' for st in sorted(subtypes)])}
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
        
        # Convert markdown in comment
        converted_comment = self.convert_markdown_links(prop_data['comment'])
        
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

<h1>{prop_name}</h1>

<div class="type-info">
    <p>{converted_comment}</p>
</div>

<div class="properties-section">
    <h2>Values expected to be one of these types</h2>
    <ul>
"""
        
        for range_type in prop_data['range_includes']:
            if range_type in self.schema_parser.types:
                content += f'        <li><a href="{{{{ site.baseurl }}}}/{range_type}">{range_type}</a></li>\n'
            else:
                content += f'        <li>{range_type}</li>\n'
        
        content += """    </ul>
</div>

<div class="properties-section">
    <h2>Used on these types</h2>
    <ul>
"""
        
        for domain_type in prop_data['domain_includes']:
            content += f'        <li><a href="{{{{ site.baseurl }}}}/{domain_type}">{domain_type}</a></li>\n'
        
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
                range_types = ', '.join([f'<a href="{{{{ site.baseurl }}}}/{rt}">{rt}</a>' 
                                       for rt in prop_data['range_includes']])
                converted_comment = self.convert_markdown_links(prop_data['comment'])
                html += f"""
            <tr>
                <td><span class="property-name"><a href="{{{{ site.baseurl }}}}/{prop_name}">{prop_name}</a></span></td>
                <td><span class="expected-type">{range_types}</span></td>
                <td>{converted_comment}</td>
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
                domain_types = ', '.join([f'<a href="{{{{ site.baseurl }}}}/{dt}" class="type-link">{dt}</a>' 
                                        for dt in prop_data['domain_includes']])
                converted_comment = self.convert_markdown_links(prop_data['comment'])
                html += f"""
            <tr>
                <td><span class="property-name"><a href="{{{{ site.baseurl }}}}/{prop_name}">{prop_name}</a></span></td>
                <td>{domain_types}</td>
                <td>{converted_comment}</td>
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
        
        print(f"Creating directories...")
        print(f"  Types directory: {types_dir}")
        print(f"  Properties directory: {props_dir}")
        
        os.makedirs(types_dir, exist_ok=True)
        os.makedirs(props_dir, exist_ok=True)
        
        # Verify directories were created
        if os.path.exists(types_dir):
            print(f"  ✓ Types directory created successfully")
        else:
            print(f"  ✗ Failed to create types directory!")
            raise Exception(f"Could not create {types_dir}")
            
        if os.path.exists(props_dir):
            print(f"  ✓ Properties directory created successfully")
        else:
            print(f"  ✗ Failed to create properties directory!")
            raise Exception(f"Could not create {props_dir}")
        
        print(f"\nGenerating Jekyll pages for {len(self.schema_parser.types)} types...")
        
        # Generate type pages
        type_count = 0
        for type_name in self.schema_parser.types:
            try:
                content = self.generate_type_page(type_name)
                filename = os.path.join(types_dir, f'{type_name}.md')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                type_count += 1
                if type_count <= 5:
                    print(f"  Created: {filename}")
            except Exception as e:
                print(f"  ERROR creating {type_name}: {e}")
                raise
        
        print(f"  Generated {type_count} type files")
        
        print(f"\nGenerating Jekyll pages for {len(self.schema_parser.properties)} properties...")
        
        # Generate property pages
        prop_count = 0
        for prop_name in self.schema_parser.properties:
            try:
                content = self.generate_property_page(prop_name)
                filename = os.path.join(props_dir, f'{prop_name}.md')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                prop_count += 1
                if prop_count <= 5:
                    print(f"  Created: {filename}")
            except Exception as e:
                print(f"  ERROR creating {prop_name}: {e}")
                raise
        
        print(f"  Generated {prop_count} property files")
        
        # Final verification
        print(f"\nFinal verification:")
        if os.path.exists(types_dir):
            type_files = len([f for f in os.listdir(types_dir) if f.endswith('.md')])
            print(f"  ✓ {types_dir} contains {type_files} files")
        else:
            print(f"  ✗ {types_dir} does not exist!")
            
        if os.path.exists(props_dir):
            prop_files = len([f for f in os.listdir(props_dir) if f.endswith('.md')])
            print(f"  ✓ {props_dir} contains {prop_files} files")
        else:
            print(f"  ✗ {props_dir} does not exist!")
        
        print(f"\nTotal generated: {len(self.schema_parser.types) + len(self.schema_parser.properties)} Jekyll pages")

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
    <link rel="stylesheet" href="{{ site.baseurl }}/schema-org.css">
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
        html += f'                        <li><a href="{{{{ site.baseurl }}}}/{type_name}">{type_name}</a></li>\n'
    
    html += f"""                    </ul>
                </div>
                
                <div class="index-section">
                    <h3>Properties ({len(properties_sorted)} total)</h3>
                    <ul class="index-list">
"""
    
    for prop_name in properties_sorted:
        html += f'                        <li><a href="{{{{ site.baseurl }}}}/{prop_name}">{prop_name}</a></li>\n'
    
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
    try:
        # Check if schema.json exists
        if not os.path.exists('data/schema.json'):
            print("ERROR: data/schema.json not found!")
            print("Current directory:", os.getcwd())
            print("Files in current directory:", os.listdir('.'))
            if os.path.exists('data'):
                print("Files in data directory:", os.listdir('data'))
            raise FileNotFoundError("data/schema.json is required")
        
        print("Found data/schema.json")
        
        # Parse schema JSON
        print("Creating schema parser...")
        schema_parser = SchemaJSONLDParser()
        
        print("Parsing schema.json...")
        schema_parser.parse_schema_json()
        
        # Generate Jekyll pages
        print("Creating Jekyll generator...")
        generator = JekyllGenerator(schema_parser)
        
        print("Generating all pages...")
        generator.generate_all_pages()
        
        # Don't generate index page - we have a custom one
        # print("Generating index page...")
        # generate_index_page(schema_parser)
        
        print("Schema.org page generation from JSON-LD complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()