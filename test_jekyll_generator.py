#!/usr/bin/env python3
"""Test the Jekyll generator locally"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the generator
    from generate_jekyll_pages import main
    
    print("Running Jekyll generator...")
    main()
    
    # Check results
    print("\nChecking generated files:")
    
    if os.path.exists('docs/_types'):
        type_files = os.listdir('docs/_types')
        print(f"✓ _types directory exists with {len(type_files)} files")
        print(f"  First 5 files: {type_files[:5]}")
    else:
        print("✗ _types directory NOT found")
    
    if os.path.exists('docs/_properties'):
        prop_files = os.listdir('docs/_properties')
        print(f"✓ _properties directory exists with {len(prop_files)} files")
        print(f"  First 5 files: {prop_files[:5]}")
    else:
        print("✗ _properties directory NOT found")
        
    # Check if Person.md was created
    if os.path.exists('docs/_types/Person.md'):
        print("\n✓ Person.md exists")
        with open('docs/_types/Person.md', 'r') as f:
            print("First 20 lines:")
            for i, line in enumerate(f):
                if i >= 20:
                    break
                print(f"  {line.rstrip()}")
    else:
        print("\n✗ Person.md NOT found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()