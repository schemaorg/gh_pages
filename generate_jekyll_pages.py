#!/usr/bin/env python3
"""
Schema.org page generator for Jekyll
Generates markdown files with front matter for Jekyll collections
"""

import os
import yaml
from generate_schema_pages import SchemaParser, ExampleParser

class JekyllGenerator:
    def __init__(self, schema_parser: SchemaParser, example_parser: ExampleParser):
        self.schema_parser = schema_parser
        self.example_parser = example_parser
        
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
        {', '.join([f'<span class="hierarchy-item"><a href="/{st}">{st}</a></span>' for st in subtypes])}
    </div>
"""
        
        content += "</div>\n\n"
        
        # Properties from this type
        if type_data['properties']:
            content += f"""
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
        <tbody>
"""
            
            for prop_name in sorted(type_data['properties']):
                if prop_name in self.schema_parser.properties:
                    prop_data = self.schema_parser.properties[prop_name]
                    range_types = ', '.join([f'<a href="/{rt}">{rt}</a>' if rt in self.schema_parser.types 
                                           else rt for rt in prop_data['range_includes']])
                    content += f"""
            <tr>
                <td><span class="property-name"><a href="/{prop_name}">{prop_name}</a></span></td>
                <td><span class="expected-type">{range_types}</span></td>
                <td>{prop_data['comment']}</td>
            </tr>
"""
            
            content += """
        </tbody>
    </table>
</div>
"""
        
        # Inherited properties
        if inherited_properties:
            for parent_type, props in inherited_properties.items():
                if props:
                    content += f"""
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
        <tbody>
"""
                    
                    for prop_name in sorted(props):
                        if prop_name in self.schema_parser.properties:
                            prop_data = self.schema_parser.properties[prop_name]
                            range_types = ', '.join([f'<a href="/{rt}">{rt}</a>' if rt in self.schema_parser.types 
                                                   else rt for rt in prop_data['range_includes']])
                            content += f"""
            <tr>
                <td><span class="property-name"><a href="/{prop_name}">{prop_name}</a></span></td>
                <td><span class="expected-type">{range_types}</span></td>
                <td>{prop_data['comment']}</td>
            </tr>
"""
                    
                    content += """
        </tbody>
    </table>
</div>
"""
        
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

def main():
    # Initialize parsers
    schema_parser = SchemaParser()
    example_parser = ExampleParser()
    
    # Parse schema and examples
    schema_parser.parse_schema_ttl()
    example_parser.parse_examples()
    
    # Generate Jekyll pages
    generator = JekyllGenerator(schema_parser, example_parser)
    generator.generate_all_pages()
    
    print("Jekyll page generation complete!")

if __name__ == "__main__":
    main()