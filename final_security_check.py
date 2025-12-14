"""
Verificación final de seguridad antes del release
"""

import os
import sys
import re

def run_security_check():
    print("="*70)
    print("🔐 VERIFICACIÓN FINAL DE SEGURIDAD - PRE-RELEASE v0.2.4")
    print("="*70)
    
    # Lista de comprobación
    checklist = {
        "engine_secure.py existe": "aeeprotocol/core/engine_secure.py",
        "client_secure.py existe": "aeeprotocol/sdk/client_secure.py",
        ".env.example existe": ".env.example",
        ".gitignore existe": ".gitignore",
    }
    
    all_ok = True
    
    # Verificar existencia
    for item, path in checklist.items():
        if os.path.exists(path):
            print(f"✅ {item}")
        else:
            print(f"❌ {item}")
            all_ok = False
    
    # Verificar contenido crítico
    print("\n📋 CONTENIDO CRÍTICO:")
    
    # 1. engine_secure.py debe tener HMAC
    if os.path.exists("aeeprotocol/core/engine_secure.py"):
        with open("aeeprotocol/core/engine_secure.py", 'r') as f:
            content = f.read()
            if "hmac.new" in content:
                print("✅ engine_secure.py: HMAC implementado")
            else:
                print("❌ engine_secure.py: FALTA HMAC")
                all_ok = False
    
    # 2. .env.example debe tener AEE_SECRET_KEY
    if os.path.exists(".env.example"):
        with open(".env.example", 'r') as f:
            content = f.read()
            if "AEE_SECRET_KEY" in content:
                print("✅ .env.example: Contiene AEE_SECRET_KEY")
            else:
                print("❌ .env.example: FALTA AEE_SECRET_KEY")
                all_ok = False
    
    # 3. .gitignore debe bloquear .env
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            content = f.read()
            if ".env" in content:
                print("✅ .gitignore: Bloquea archivos .env")
            else:
                print("❌ .gitignore: NO bloquea .env")
                all_ok = False
    
    # 4. Verificar que no hay claves hardcodeadas
    print("\n🔍 BUSCANDO CLAVES HARDCODEADAS (seguridad):")
    
    dangerous_patterns = [
        r"secret_key\s*=\s*['\"][^'\"]{10,}['\"]",  # Claves en strings
        r"token_bytes\(\)",  # Generación sin almacenamiento seguro
        r"user_id\s*=\s*35664619",  # Tu user_id de prueba hardcodeado
    ]
    
    safe = True
    for root, dirs, files in os.walk("aeeprotocol"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in dangerous_patterns:
                        if re.search(pattern, content):
                            print(f"⚠️  {filepath}: Posible clave hardcodeada")
                            safe = False
    
    if safe:
        print("✅ No se encontraron claves hardcodeadas")
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL DE SEGURIDAD")
    print("="*70)
    
    if all_ok and safe:
        print("✅ ¡TODO CORRECTO! Listo para Release v0.2.4")
        print("\n🎯 Próximos pasos:")
        print("1. git push origin main")
        print("2. Crear Release v0.2.4 en GitHub")
        print("3. Actualizar README con instrucciones de seguridad")
        print("4. Publicar en redes")
    else:
        print("❌ PROBLEMAS DE SEGURIDAD DETECTADOS")
        print("\n⚠️  Corrige los problemas antes del release.")
    
    print("="*70)
    
    return all_ok and safe

if __name__ == "__main__":
    success = run_security_check()
    sys.exit(0 if success else 1)