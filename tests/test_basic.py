"""Basic tests for AEE Protocol v0.5 structure"""
import sys
import os

def test_project_structure():
"""Test that project has correct structure"""
print("🧪 Testing project structure...")

text
required_paths = [
    "src/aeeprotocol",
    "src/aeeprotocol/__init__.py",
    "tests",
    "examples",
    "pyproject.toml",
    "README.md"
]

all_exist = True
for path in required_paths:
    if os.path.exists(path):
        print(f"  ✅ {path}")
    else:
        print(f"  ❌ {path}")
        all_exist = False

return all_exist
def test_basic_import():
"""Test basic import functionality"""
print("\n🧪 Testing imports...")

text
# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import aeeprotocol
    print(f"  ✅ Imported aeeprotocol")
    print(f"     Version: {aeeprotocol.__version__}")
    print(f"     Author: {aeeprotocol.__author__}")
    
    # Check protocol info
    info = aeeprotocol.get_info()
    print(f"     Algorithm: {info['algorithm']}")
    
    return True
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    return False
def test_kyber_dependency():
"""Test if Kyber dependency is available"""
print("\n🧪 Checking Kyber dependency...")

text
try:
    import liboqs
    print(f"  ✅ liboqs available")
    
    # Check for Kyber-768
    from liboqs import KeyEncapsulationMechanism
    kems = KeyEncapsulationMechanism.get_supported_kems()
    if "Kyber768" in kems:
        print(f"  ✅ Kyber-768 supported")
        return True
    else:
        print(f"  ⚠️  Kyber-768 not in supported KEMs")
        return False
except ImportError:
    print(f"  ⚠️  liboqs not installed (required for full functionality)")
    print(f"     Install: pip install liboqs-python")
    return False
def main():
"""Run all basic tests"""
print("=" * 60)
print("AEE Protocol v0.5 - Basic Test Suite")
print("=" * 60)

text
results = []
results.append(test_project_structure())
results.append(test_basic_import())
results.append(test_kyber_dependency())

print("\n" + "=" * 60)

if all(results):
    print("🎉 All tests passed!")
    return 0
elif results[0] and results[1]:
    print("✅ Basic structure and imports working")
    print("⚠️  Kyber dependency needed for full functionality")
    return 0
else:
    print("❌ Critical tests failed")
    return 1
if name == "main":
sys.exit(main())
