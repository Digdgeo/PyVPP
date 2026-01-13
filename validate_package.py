#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package Validation Script for PyVPP

Verifies that the package is ready for distribution by checking:
- File structure
- Version consistency
- Import capability
- Required files present
"""

import os
import sys
from pathlib import Path
import re

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")
    return False

def print_warning(text):
    print(f"⚠ {text}")

def get_version_from_file(filepath, pattern):
    """Extract version from a file using a regex pattern"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            match = re.search(pattern, content)
            if match:
                return match.group(1)
    except Exception as e:
        print_error(f"Error reading {filepath}: {e}")
    return None

def check_file_structure():
    """Check that all required files are present"""
    print_header("1. Checking File Structure")
    
    required_files = {
        'README.md': 'Main documentation',
        'LICENSE': 'License file',
        'CHANGELOG.md': 'Change history',
        'pyproject.toml': 'Poetry configuration',
        'setup.py': 'Setup configuration',
        'requirements.txt': 'Dependencies list',
        'MANIFEST.in': 'Package manifest',
        'pyvpp/__init__.py': 'Package init',
        'pyvpp/WekeoDownload.py': 'Main module',
    }
    
    optional_files = {
        '.gitignore': 'Git ignore file',
        'BUILD_INSTRUCTIONS.md': 'Build instructions',
        'examples/basic_usage.py': 'Example script',
        'examples/README.md': 'Examples documentation',
    }
    
    all_ok = True
    
    for filepath, description in required_files.items():
        if Path(filepath).exists():
            print_success(f"{filepath} - {description}")
        else:
            print_error(f"MISSING: {filepath} - {description}")
            all_ok = False
    
    print("\nOptional files:")
    for filepath, description in optional_files.items():
        if Path(filepath).exists():
            print_success(f"{filepath} - {description}")
        else:
            print_warning(f"Not found: {filepath} - {description}")
    
    return all_ok

def check_version_consistency():
    """Check that version numbers are consistent across files"""
    print_header("2. Checking Version Consistency")
    
    versions = {}
    
    # Check pyproject.toml
    version = get_version_from_file('pyproject.toml', r'version\s*=\s*"([^"]+)"')
    if version:
        versions['pyproject.toml'] = version
        print(f"pyproject.toml: {version}")
    
    # Check setup.py
    version = get_version_from_file('setup.py', r"version\s*=\s*'([^']+)'")
    if version:
        versions['setup.py'] = version
        print(f"setup.py: {version}")
    
    # Check __init__.py
    version = get_version_from_file('pyvpp/__init__.py', r"__version__\s*=\s*'([^']+)'")
    if version:
        versions['pyvpp/__init__.py'] = version
        print(f"pyvpp/__init__.py: {version}")
    
    # Check consistency
    if len(set(versions.values())) == 1:
        print_success(f"All versions match: {list(versions.values())[0]}")
        return True
    else:
        print_error("Version mismatch detected:")
        for file, ver in versions.items():
            print(f"  {file}: {ver}")
        return False

def check_imports():
    """Check that the package can be imported"""
    print_header("3. Checking Import Capability")
    
    # Add current directory to path
    sys.path.insert(0, str(Path.cwd()))
    
    try:
        import pyvpp
        print_success("Package imports successfully")
        
        # Check version
        if hasattr(pyvpp, '__version__'):
            print_success(f"Version accessible: {pyvpp.__version__}")
        else:
            print_warning("__version__ attribute not found")
        
        # Check main class
        if hasattr(pyvpp, 'wekeo_download'):
            print_success("wekeo_download class found")
        else:
            print_error("wekeo_download class not found")
            return False
        
        # Check functions
        functions = ['create_hdarc', 'delete_hdarc', 'clean_old_hdarc']
        for func in functions:
            if hasattr(pyvpp, func):
                print_success(f"{func} function found")
            else:
                print_warning(f"{func} function not found")
        
        return True
        
    except ImportError as e:
        print_error(f"Failed to import package: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error during import: {e}")
        return False

def check_readme():
    """Check README.md content"""
    print_header("4. Checking README Content")
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        checks = {
            'Installation': 'pip install pyvpp' in content,
            'Quick Start': 'Quick Start' in content or 'quick start' in content.lower(),
            'Examples': 'example' in content.lower(),
            'License': 'license' in content.lower() or 'MIT' in content,
            'Version 0.1.9': '0.1.9' in content,
        }
        
        all_ok = True
        for check, result in checks.items():
            if result:
                print_success(f"{check} section present")
            else:
                print_warning(f"{check} section may be missing")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_error(f"Error checking README: {e}")
        return False

def check_dependencies():
    """Check that dependencies are properly specified"""
    print_header("5. Checking Dependencies")
    
    # Expected dependencies
    expected_deps = ['hda', 'deims', 'geopandas', 'pyproj', 'rasterio', 'requests', 'fiona']
    
    # Check pyproject.toml
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        
        for dep in expected_deps:
            if dep in content:
                print_success(f"{dep} specified in pyproject.toml")
            else:
                print_warning(f"{dep} not found in pyproject.toml")
    except Exception as e:
        print_error(f"Error checking pyproject.toml: {e}")
        return False
    
    # Check requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        print("\nrequirements.txt:")
        for dep in expected_deps:
            if dep in content:
                print_success(f"{dep} specified")
            else:
                print_warning(f"{dep} not found")
    except Exception as e:
        print_error(f"Error checking requirements.txt: {e}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("\n" + "="*60)
    print("PyVPP Package Validation")
    print("="*60)
    
    results = {}
    
    # Change to package root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\nWorking directory: {Path.cwd()}")
    
    # Run checks
    results['structure'] = check_file_structure()
    results['version'] = check_version_consistency()
    results['imports'] = check_imports()
    results['readme'] = check_readme()
    results['dependencies'] = check_dependencies()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check.capitalize():20} {status}")
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Package is ready for distribution!")
        print("="*60)
        print("\nNext steps:")
        print("1. Review CHANGELOG.md")
        print("2. Commit and tag: git tag v0.1.9")
        print("3. Build: python -m build")
        print("4. Test: pip install dist/pyvpp-0.1.9-py3-none-any.whl")
        print("5. Upload to Test PyPI")
        print("6. Upload to PyPI")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please fix issues before distributing")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
