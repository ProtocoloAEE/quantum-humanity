"""Basic structure tests for AEE Protocol v0.5"""
import os
import sys

def test_project_structure():
    """Test that the project has the correct structure"""
    print("Testing AEE Protocol structure...")
    
    required_paths = [
        "src/aeeprotocol",
        "src/aeeprotocol/__init__.py",
        "src/aeeprotocol/core/__init__.py",
        "src/aeeprotocol/api/__init__.py",
        "src/aeeprotocol/sdk/__init__.py",
        "tests",
        "examples",
        "pyproject.toml",
        "README.md",
        "requirements.txt"
    ]
    
    all_ok = True
    for path in required_paths:
        if os.path.exists(path):
            print(f"  [+] {path}")
        else:
            print(f"  [x] {path} (missing)")
            all_ok = False
    
    return all_ok

def test_python_files():
    """Count Python files in key directories"""
    print("\nPython file counts:")
    
    directories = {
        "src/aeeprotocol": "Main package",
        "tests": "Test suite",
        "examples": "Examples",
        "scripts": "Utility scripts"
    }
    
    for dir_path, description in directories.items():
        if os.path.exists(dir_path):
            py_files = [f for f in os.listdir(dir_path) if f.endswith('.py')]
            print(f"  - {dir_path}: {len(py_files)} files ({description})")
        else:
            print(f"  - {dir_path}: Directory missing")
    
    return True

def main():
    """Run all structure tests"""
    print("=" * 60)
    print("AEE Protocol v0.5 - Structure Validation")
    print("=" * 60)
    
    # Add src to Python path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    # Run tests
    structure_ok = test_project_structure()
    files_ok = test_python_files()
    
    print("\n" + "=" * 60)
    
    if structure_ok and files_ok:
        print("Structure validation PASSED!")
        print("\nNext: Install with 'pip install -e .'")
        return 0
    else:
        print("Structure validation has issues")
        print("Check missing files/directories above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
