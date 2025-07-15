#!/usr/bin/env python3
"""
Schema.org page generator
Parses schema.ttl and generates HTML pages for all vocabulary items
"""

import re
import os
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

class SchemaParser:
    def __init__(self):
        self.types = {}  # type_name -> {label, comment, subclass_of, properties}
        self.properties = {}  # property_name -> {label, comment, domain_includes, range_includes}
        self.inverse_properties = defaultdict(list)  # type -> list of properties that accept this type
        
    def parse_schema_ttl(self, filename='schema.ttl'):
        """Parse the schema.ttl file and extract types and properties"""
        print(f"Parsing {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse types (classes)
        type_pattern = r':(\w+)\s+a\s+rdfs:Class\s*;(.*?)(?=\n:|\n\n|\Z)'
        for match in re.finditer(type_pattern, content, re.DOTALL):
            type_name = match.group(1)
            type_def = match.group(2)
            
            # Extract label
            label_match = re.search(r'rdfs:label\s+"([^"]+)"', type_def)
            label = label_match.group(1) if label_match else type_name
            
            # Extract comment
            comment_match = re.search(r'rdfs:comment\s+"([^"]+)"', type_def)
            comment = comment_match.group(1) if comment_match else ""
            
            # Extract subclass
            subclass_match = re.search(r'rdfs:subClassOf\s+:(\w+)', type_def)
            subclass_of = subclass_match.group(1) if subclass_match else None
            
            self.types[type_name] = {
                'label': label,
                'comment': comment,
                'subclass_of': subclass_of,
                'properties': []
            }
        
        # Parse properties
        prop_pattern = r':(\w+)\s+a\s+rdf:Property\s*;(.*?)(?=\n:|\n\n|\Z)'
        for match in re.finditer(prop_pattern, content, re.DOTALL):
            prop_name = match.group(1)
            prop_def = match.group(2)
            
            # Extract label
            label_match = re.search(r'rdfs:label\s+"([^"]+)"', prop_def)
            label = label_match.group(1) if label_match else prop_name
            
            # Extract comment
            comment_match = re.search(r'rdfs:comment\s+"([^"]+)"', prop_def)
            comment = comment_match.group(1) if comment_match else ""
            
            # Extract domain includes (which types can use this property)
            domain_includes = []
            domain_matches = re.findall(r':domainIncludes\s+:(\w+)', prop_def)
            domain_includes.extend(domain_matches)
            
            # Extract range includes (what types this property accepts)
            range_includes = []
            range_matches = re.findall(r':rangeIncludes\s+:(\w+)', prop_def)
            range_includes.extend(range_matches)
            
            self.properties[prop_name] = {
                'label': label,
                'comment': comment,
                'domain_includes': domain_includes,
                'range_includes': range_includes
            }
            
            # Build inverse property mapping
            for range_type in range_includes:
                if range_type in self.types:
                    self.inverse_properties[range_type].append(prop_name)
        
        # Add properties to types
        for prop_name, prop_data in self.properties.items():
            for domain_type in prop_data['domain_includes']:
                if domain_type in self.types:
                    self.types[domain_type]['properties'].append(prop_name)
        
        print(f"Parsed {len(self.types)} types and {len(self.properties)} properties")

class ExampleParser:
    def __init__(self):
        self.examples = defaultdict(list)  # type_name -> list of examples
        
    def parse_examples(self, examples_dir='examples'):
        """Parse all example files and extract examples by type"""
        print("Parsing examples...")
        
        example_files = [f for f in os.listdir(examples_dir) if f.endswith('.txt')]
        
        for filename in example_files:
            filepath = os.path.join(examples_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find examples in the format: TYPES: TypeName
            # Then extract the JSON-LD, Microdata, and RDFa examples that follow
            type_pattern = r'TYPES:\s*([^\n]+)'
            
            sections = re.split(r'TYPES:\s*', content)[1:]  # Skip first empty section
            
            for section in sections:
                lines = section.split('\n')
                if not lines:
                    continue
                    
                type_line = lines[0].strip()
                types = [t.strip() for t in type_line.split(',')]
                
                # Extract examples from this section
                example_content = '\n'.join(lines[1:])
                
                # Look for JSON-LD examples
                jsonld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', example_content, re.DOTALL)
                
                # Look for Microdata examples  
                microdata_matches = re.findall(r'<div[^>]*itemscope[^>]*itemtype="https://schema\.org/([^"]+)"[^>]*>(.*?)</div>', example_content, re.DOTALL)
                
                for type_name in types:
                    type_name = type_name.strip()
                    if type_name:
                        for jsonld in jsonld_matches:
                            self.examples[type_name].append({
                                'format': 'jsonld',
                                'content': jsonld.strip(),
                                'source_file': filename
                            })
                        
                        for microdata_type, microdata_content in microdata_matches:
                            if microdata_type == type_name:
                                self.examples[type_name].append({
                                    'format': 'microdata',
                                    'content': microdata_content.strip(),
                                    'source_file': filename
                                })
        
        print(f"Parsed examples for {len(self.examples)} types")

class HTMLGenerator:
    def __init__(self, schema_parser: SchemaParser, example_parser: ExampleParser):
        self.schema_parser = schema_parser
        self.example_parser = example_parser
        
    def generate_type_page(self, type_name: str) -> str:
        """Generate HTML page for a schema type"""
        type_data = self.schema_parser.types[type_name]
        
        # Get inherited properties from parent types
        inherited_properties = self.get_inherited_properties(type_name)
        
        # Get properties where this type can be used as a value
        inverse_properties = self.schema_parser.inverse_properties.get(type_name, [])
        
        # Get examples for this type
        examples = self.example_parser.examples.get(type_name, [])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{type_name} - schema.org Type</title>
    <link rel="stylesheet" href="schema-org.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>schema.org</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="breadcrumb">
            <a href="index.html">Home</a>"""
        
        # Add breadcrumb trail for inheritance
        parent = type_data['subclass_of']
        breadcrumb_trail = []
        while parent:
            breadcrumb_trail.append(parent)
            parent = self.schema_parser.types.get(parent, {}).get('subclass_of')
        
        for ancestor in reversed(breadcrumb_trail):
            html += f' &gt; <a href="{ancestor}.html">{ancestor}</a>'
        
        html += f' &gt; {type_name}'
        html += '</div>'
        
        html += f"""
        <div class="main-content">
            <h1>{type_name}</h1>
            
            <div class="type-info">
                <p><strong>{type_data['comment']}</strong></p>"""
        
        if type_data['subclass_of']:
            html += f"""
                <div class="type-hierarchy">
                    <strong>Subclass of:</strong>
                    <span class="hierarchy-item"><a href="{type_data['subclass_of']}.html">{type_data['subclass_of']}</a></span>
                </div>"""
        
        # Find subtypes
        subtypes = [t for t, data in self.schema_parser.types.items() 
                   if data['subclass_of'] == type_name]
        if subtypes:
            html += f"""
                <div class="type-hierarchy">
                    <strong>More specific types:</strong>
                    {', '.join([f'<span class="hierarchy-item"><a href="{st}.html">{st}</a></span>' for st in subtypes])}
                </div>"""
        
        html += '</div>'
        
        # Properties from this type
        if type_data['properties']:
            html += f"""
            <div class="properties-section">
                <h2>Properties from {type_name}</h2>
                <table class="property-table">
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Expected Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for prop_name in sorted(type_data['properties']):
                if prop_name in self.schema_parser.properties:
                    prop_data = self.schema_parser.properties[prop_name]
                    range_types = ', '.join([f'<a href="{rt}.html">{rt}</a>' if rt in self.schema_parser.types 
                                           else rt for rt in prop_data['range_includes']])
                    html += f"""
                        <tr>
                            <td><span class="property-name"><a href="{prop_name}.html">{prop_name}</a></span></td>
                            <td><span class="expected-type">{range_types}</span></td>
                            <td>{prop_data['comment']}</td>
                        </tr>"""
            
            html += """
                    </tbody>
                </table>
            </div>"""
        
        # Inherited properties
        if inherited_properties:
            for parent_type, props in inherited_properties.items():
                if props:
                    html += f"""
            <div class="properties-section">
                <h2>Properties from {parent_type}</h2>
                <table class="property-table">
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Expected Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>"""
                    
                    for prop_name in sorted(props):
                        if prop_name in self.schema_parser.properties:
                            prop_data = self.schema_parser.properties[prop_name]
                            range_types = ', '.join([f'<a href="{rt}.html">{rt}</a>' if rt in self.schema_parser.types 
                                                   else rt for rt in prop_data['range_includes']])
                            html += f"""
                        <tr>
                            <td><span class="property-name"><a href="{prop_name}.html">{prop_name}</a></span></td>
                            <td><span class="expected-type">{range_types}</span></td>
                            <td>{prop_data['comment']}</td>
                        </tr>"""
                    
                    html += """
                    </tbody>
                </table>
            </div>"""
        
        # Properties where this type can be used as a value
        if inverse_properties:
            html += f"""
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
                    <tbody>"""
            
            for prop_name in sorted(inverse_properties):
                if prop_name in self.schema_parser.properties:
                    prop_data = self.schema_parser.properties[prop_name]
                    domain_types = ', '.join([f'<a href="{dt}.html" class="type-link">{dt}</a>' 
                                            for dt in prop_data['domain_includes']])
                    html += f"""
                        <tr>
                            <td><span class="property-name"><a href="{prop_name}.html">{prop_name}</a></span></td>
                            <td>{domain_types}</td>
                            <td>{prop_data['comment']}</td>
                        </tr>"""
            
            html += """
                    </tbody>
                </table>
            </div>"""
        
        # Examples section
        if examples:
            html += f"""
            <div class="examples-section">
                <h2>Examples</h2>
                <div class="example-tabs">
                    <div class="example-tab active" onclick="showExample('jsonld')">JSON-LD</div>
                    <div class="example-tab" onclick="showExample('microdata')">Microdata</div>
                </div>"""
            
            # JSON-LD examples
            jsonld_examples = [ex for ex in examples if ex['format'] == 'jsonld']
            if jsonld_examples:
                html += f"""
                <div id="jsonld-example" class="example-content">
                    <h3>JSON-LD</h3>
                    <pre><code>{jsonld_examples[0]['content']}</code></pre>
                </div>"""
            else:
                html += f"""
                <div id="jsonld-example" class="example-content">
                    <h3>JSON-LD</h3>
                    <pre><code>// No JSON-LD example available for {type_name}</code></pre>
                </div>"""
            
            # Microdata examples
            microdata_examples = [ex for ex in examples if ex['format'] == 'microdata']
            if microdata_examples:
                html += f"""
                <div id="microdata-example" class="example-content" style="display:none;">
                    <h3>Microdata</h3>
                    <pre><code>{microdata_examples[0]['content']}</code></pre>
                </div>"""
            else:
                html += f"""
                <div id="microdata-example" class="example-content" style="display:none;">
                    <h3>Microdata</h3>
                    <pre><code><!-- No Microdata example available for {type_name} --></code></pre>
                </div>"""
            
            html += '</div>'
        
        html += """
        </div>
    </div>
    
    <script>
        function showExample(format) {
            document.getElementById('jsonld-example').style.display = 'none';
            document.getElementById('microdata-example').style.display = 'none';
            
            var tabs = document.querySelectorAll('.example-tab');
            tabs.forEach(function(tab) {
                tab.classList.remove('active');
            });
            
            document.getElementById(format + '-example').style.display = 'block';
            event.target.classList.add('active');
        }
    </script>
</body>
</html>"""
        
        return html
    
    def generate_property_page(self, prop_name: str) -> str:
        """Generate HTML page for a schema property"""
        prop_data = self.schema_parser.properties[prop_name]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prop_name} - schema.org Property</title>
    <link rel="stylesheet" href="schema-org.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>schema.org</h1>
        </div>
    </header>
    
    <div class="container">
        <div class="breadcrumb">
            <a href="index.html">Home</a> &gt; {prop_name}
        </div>
        
        <div class="main-content">
            <h1>{prop_name}</h1>
            
            <div class="type-info">
                <p><strong>{prop_data['comment']}</strong></p>
            </div>
            
            <div class="properties-section">
                <h2>Values expected to be one of these types</h2>
                <ul>"""
        
        for range_type in prop_data['range_includes']:
            if range_type in self.schema_parser.types:
                html += f'<li><a href="{range_type}.html">{range_type}</a></li>'
            else:
                html += f'<li>{range_type}</li>'
        
        html += """
                </ul>
            </div>
            
            <div class="properties-section">
                <h2>Used on these types</h2>
                <ul>"""
        
        for domain_type in prop_data['domain_includes']:
            html += f'<li><a href="{domain_type}.html">{domain_type}</a></li>'
        
        html += """
                </ul>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def get_inherited_properties(self, type_name: str) -> Dict[str, List[str]]:
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
        """Generate HTML pages for all types and properties"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating pages for {len(self.schema_parser.types)} types...")
        
        # Generate type pages
        for type_name in self.schema_parser.types:
            html = self.generate_type_page(type_name)
            filename = os.path.join(output_dir, f'{type_name}.html')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Generating pages for {len(self.schema_parser.properties)} properties...")
        
        # Generate property pages
        for prop_name in self.schema_parser.properties:
            html = self.generate_property_page(prop_name)
            filename = os.path.join(output_dir, f'{prop_name}.html')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Generated {len(self.schema_parser.types) + len(self.schema_parser.properties)} pages in {output_dir}/")

def main():
    # Initialize parsers
    schema_parser = SchemaParser()
    example_parser = ExampleParser()
    
    # Parse schema and examples
    schema_parser.parse_schema_ttl()
    example_parser.parse_examples()
    
    # Generate HTML pages
    generator = HTMLGenerator(schema_parser, example_parser)
    generator.generate_all_pages()
    
    print("Schema.org page generation complete!")

if __name__ == "__main__":
    main()