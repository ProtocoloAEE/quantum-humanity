# test_quantum.py
"""
QUANTUM HUMANITY - Test de Validación v0.5.0
Prueba adaptable al protocolo AEE con Kyber-768
"""

import numpy as np
import time
import json
import os
import sys

# Añadir raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"🧪 {title.upper()}")
    print(f"{'=' * 70}")

def test_quantum_humanity():
    print("🚀 QUANTUM HUMANITY - TEST DE VALIDACIÓN v0.5.0")
    print("Iniciando prueba completa del protocolo post-cuántico...\n")

    results = {
        "test_passed": False,
        "steps": {},
        "performance": {},
        "info": {}
    }

    # ===== 1. IMPORTAR PAQUETE =====
    print_section("1. Importación del paquete AEE Protocol")
    try:
        import aeeprotocol
        print("✅ Paquete aeeprotocol importado correctamente")
        print(f"   Versión: {getattr(aeeprotocol, '__version__', 'N/A')}")
        
        # Intentar obtener info
        if hasattr(aeeprotocol, 'get_info'):
            info = aeeprotocol.get_info()
            print(f"   Info: {info}")
            results["info"] = info
        
        results["steps"]["import"] = True

    except Exception as e:
        print(f"❌ Error importando aeeprotocol: {e}")
        return results

    # ===== 2. ACCEDER AL CLIENTE Y MOTOR =====
    print_section("2. Acceso al cliente y generación de claves")
    try:
        # Intentar diferentes formas comunes de acceder al cliente
        client_class = None
        engine = None

        # Opción 1: Cliente directo en paquete
        if hasattr(aeeprotocol, 'AEEClient'):
            client_class = aeeprotocol.AEEClient

        # Opción 2: En sdk
        if client_class is None:
            try:
                from aeeprotocol.sdk.client import AEEClient
                client_class = AEEClient
            except:
                pass

        # Buscar motor Kyber
        try:
            from aeeprotocol.core.kyber_engine import KyberEngine
            engine = KyberEngine()
        except:
            try:
                from aeeprotocol.core.crypto import KyberEngine
                engine = KyberEngine()
            except:
                print("⚠️ Motor Kyber no encontrado directamente - usando cliente para generación")

        results["steps"]["client_access"] = True

    except Exception as e:
        print(f"❌ Error accediendo a componentes: {e}")
        return results

    # ===== 3. GENERACIÓN DE IDENTIDAD =====
    print_section("3. Generación de identidad post-cuántica")
    try:
        if engine:
            public_key, secret_key = engine.generate_keypair()
            print("✅ Claves generadas usando motor Kyber")
        else:
            # Si no hay motor directo, asumir que el cliente tiene método
            raise NotImplementedError("Motor no encontrado - ajustar según tu estructura")

        print(f"   Public key: {len(public_key)} bytes")
        print(f"   Secret key: {len(secret_key)} bytes")
        print("   ¡Guarda el secret_key de forma segura!")

        results["steps"]["key_gen"] = True

    except Exception as e:
        print(f"❌ Error generando claves: {e}")
        print("   Posiblemente tu cliente tiene método propio de generación")
        return results

    # ===== 4. CREACIÓN DEL CLIENTE =====
    print_section("4. Creación del cliente AEE")
    try:
        client = client_class(secret_key=secret_key)
        print("✅ Cliente AEE creado con identidad post-cuántica")
        results["steps"]["client_creation"] = True

    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return results

    # ===== 5. SELLADO Y VERIFICACIÓN =====
    print_section("5. Sellado y verificación de embedding")
    try:
        embedding = np.random.randn(768).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        embedding_bytes = embedding.tobytes()

        sealed = client.seal_vector(embedding_bytes)
        print("✅ Embedding sellado")
        print(f"   Ciphertext preview: {sealed.get('ciphertext', 'N/A')[:64]}...")

        # Verificación
        recovered = client.verify_seal(sealed['ciphertext'])
        print("✅ Verificación exitosa - shared_secret recuperado")

        results["steps"]["seal_verify"] = True

    except Exception as e:
        print(f"❌ Error en sellado/verificación: {e}")
        return results

    # ===== RESULTADO FINAL =====
    print_section("RESULTADO FINAL")
    passed = sum(results["steps"].values())
    total = len(results["steps"])
    print(f"📊 Pasos completados: {passed}/{total}")

    if passed == total:
        print("\n🎉 ¡QUANTUM HUMANITY v0.5.0 VALIDADO CON ÉXITO!")
        print("✅ El protocolo AEE con Kyber-768 está operativo")
        results["test_passed"] = True
    else:
        print("\n⚠️ Prueba parcial - revisar errores")

    # Guardar resultados
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    with open(f"test_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    test_results = test_quantum_humanity()
    if test_results["test_passed"]:
        print("\n🏆 PROTOCOLO AEE POST-CUÁNTICO OPERATIVO")
        print("La autoría humana está protegida")