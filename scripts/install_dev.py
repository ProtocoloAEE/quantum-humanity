#!/usr/bin/env python3
"""
Easy installation script for AEE Protocol v0.5
Run: python install_dev.py
"""

import subprocess
import sys
import os

def run_command(cmd, desc):
"""Run a command and show status"""
print(f"\n📦 {desc}...")
print(f" $ {cmd}")

text
try:
    result = subprocess.run(cmd, shell=True, check=True, 
                          capture_output=True, text=True)
    print(f"   ✅ Success")
    return True
except subprocess.CalledProcessError as e:
    print(f"   ❌ Failed: {e}")
    if e.stderr:
        print(f"   Error details: {e.stderr[:200]}")
    return False
def main():
print("=" * 60)
print("AEE Protocol v0.5 - Easy Installation")
print("=" * 60)

text
# 1. Update pip
run_command("python -m pip install --upgrade pip", "Updating pip")

# 2. Install in development mode
if not run_command("pip install -e .", "Installing in development mode"):
    print("\n⚠️  Trying alternative installation...")
    run_command("pip install .", "Installing normally")

# 3. Install core dependencies
print("\n🔧 Installing core dependencies...")
run_command("pip install liboqs-python", "Installing liboqs (Kyber-768)")
run_command("pip install numpy", "Installing numpy")
run_command("pip install cryptography", "Installing cryptography")

# 4. Ask about optional dependencies
print("\n📦 Optional dependencies:")

if input("Install API dependencies (Flask)? [y/N]: ").lower() == 'y':
    run_command("pip install flask flask-cors", "Installing API dependencies")

if input("Install development tools? [y/N]: ").lower() == 'y':
    run_command("pip install pytest black flake8", "Installing dev tools")

# 5. Test installation
print("\n🔍 Testing installation...")
test_code = '''
try:
import aeeprotocol
print(f"✅ AEE Protocol v{aeeprotocol.version} installed!")
print(f" Author: {aeeprotocol.author}")
print(f" Algorithm: {aeeprotocol.get_info()['algorithm']}")

text
# Try to import Kyber
try:
    from liboqs import KeyEncapsulation
    print("✅ Kyber-768 dependencies available")
except:
    print("⚠️  Kyber dependencies may need restart")
    
except Exception as e:
print(f"❌ Error: {e}")
'''

text
result = subprocess.run([sys.executable, "-c", test_code], 
                      capture_output=True, text=True)
print(result.stdout)

if result.stderr:
    print("⚠️  Warnings:", result.stderr)

# 6. Show next steps
print("\n" + "=" * 60)
print("🎉 Installation complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Run tests: python -m pytest tests/")
print("2. Try example: python examples/basic_usage.py")
print("3. Check structure: python tests/test_basic.py")
print("\nFor API:")
print("  python src/aeeprotocol/api/server.py")
print("\nHappy coding! 🚀")
if name == "main":
main()
