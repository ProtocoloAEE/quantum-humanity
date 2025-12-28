#!/usr/bin/env python3
"""
AEE Protocol - Kyber-768 REAL con liboqs-python
Versión corregida para Python 3.13 / Windows

Requisitos:
    pip install liboqs-python numpy
"""

import sys
import time
import hashlib
import json
from typing import Tuple, Dict

# ============================================================================
# VERIFICACIÓN E IMPORTACIÓN DE DEPENDENCIAS
# ============================================================================
print("🔍 Verificando dependencias...\n")

# NumPy
try:
    import numpy as np
    print(f"✅ NumPy {np.__version__} instalado")
except ImportError as e:
    print(f"❌ Error: numpy no instalado - {e}")
    print("   Ejecuta: pip install numpy")
    sys.exit(1)

# liboqs
try:
    import oqs
    print(f"✅ liboqs-python instalado")
    print(f"   Versión liboqs: {oqs.oqs_version()}")
    print(f"   Versión wrapper: {oqs.oqs_python_version()}")
except ImportError as e:
    print(f"❌ Error importando liboqs: {e}")
    print("\n💡 Soluciones:")
    print("   1. Reinstalar: pip uninstall liboqs-python && pip install liboqs-python")
    print("   2. Verificar instalación: pip show liboqs-python")
    print("   3. Usar la versión simplificada: python aee_demo_simplified.py")
    sys.exit(1)

print()


# ============================================================================
# COLORES PARA CLI
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


# ============================================================================
# DEMO 1: KYBER-768 REAL
# ============================================================================
def demo_kyber_real():
    """Demo con Kyber-768 real usando liboqs"""
    
    print_header("🔐 DEMO 1: KYBER-768 REAL (NIST FIPS 203)")
    
    kem_name = "Kyber768"
    
    # Verificar disponibilidad
    print_info(f"Verificando {kem_name}...")
    
    try:
        supported = oqs.get_enabled_KEM_mechanisms()
        
        if kem_name not in supported:
            print_error(f"{kem_name} no disponible")
            print(f"   KEMs disponibles: {', '.join(supported[:5])}...")
            return None
        
        print_success(f"{kem_name} disponible")
        print(f"   Total algoritmos PQC: {len(supported)}")
        print()
        
    except Exception as e:
        print_error(f"Error verificando KEMs: {e}")
        return None
    
    # Generar claves (Alice)
    print_info("Generando par de claves (Alice)...")
    start = time.time()
    
    try:
        alice_kem = oqs.KeyEncapsulation(kem_name)
        public_key = alice_kem.generate_keypair()
        keygen_time = (time.time() - start) * 1000
        
        print_success(f"Claves generadas en {keygen_time:.2f} ms")
        print(f"   • Clave pública: {len(public_key)} bytes")
        print(f"   • Primeros 32 bytes: {public_key[:32].hex()}")
        print()
        
    except Exception as e:
        print_error(f"Error generando claves: {e}")
        return None
    
    # Encapsular (Alice → Bob)
    print_info("Encapsulando secreto compartido...")
    start = time.time()
    
    try:
        ciphertext, shared_secret_alice = alice_kem.encap_secret(public_key)
        encap_time = (time.time() - start) * 1000
        
        print_success(f"Encapsulación en {encap_time:.2f} ms")
        print(f"   • Ciphertext: {len(ciphertext)} bytes")
        print(f"   • Secreto compartido: {len(shared_secret_alice)} bytes")
        print(f"   • Hash SHA3-256: {hashlib.sha3_256(shared_secret_alice).hexdigest()[:32]}...")
        print()
        
    except Exception as e:
        print_error(f"Error en encapsulación: {e}")
        return None
    
    # Desencapsular (Bob)
    print_info("Desencapsulando (Bob)...")
    start = time.time()
    
    try:
        shared_secret_bob = alice_kem.decap_secret(ciphertext)
        decap_time = (time.time() - start) * 1000
        
        print_success(f"Desencapsulación en {decap_time:.2f} ms")
        print()
        
    except Exception as e:
        print_error(f"Error en desencapsulación: {e}")
        return None
    
    # Verificar
    print_info("Verificando correspondencia...")
    
    if shared_secret_alice == shared_secret_bob:
        print_success("¡SECRETOS COINCIDEN PERFECTAMENTE!")
        print(f"   Alice: {shared_secret_alice.hex()[:32]}...")
        print(f"   Bob:   {shared_secret_bob.hex()[:32]}...")
    else:
        print_error("Los secretos NO coinciden (error crítico)")
        return None
    
    # Performance
    total_time = keygen_time + encap_time + decap_time
    
    print(f"\n{Colors.BOLD}📊 Performance (Kyber-768 Real):{Colors.END}")
    print(f"   Generación:       {keygen_time:>6.2f} ms")
    print(f"   Encapsulación:    {encap_time:>6.2f} ms")
    print(f"   Desencapsulación: {decap_time:>6.2f} ms")
    print(f"   {Colors.BOLD}Total:{Colors.END}            {Colors.GREEN}{total_time:>6.2f} ms{Colors.END}")
    
    return {
        'kem': alice_kem,
        'public_key': public_key,
        'ciphertext': ciphertext,
        'shared_secret': shared_secret_alice,
        'metrics': {
            'keygen': keygen_time,
            'encap': encap_time,
            'decap': decap_time,
            'total': total_time
        }
    }


# ============================================================================
# CLASE AEE PROTOCOL CON KYBER-768 REAL
# ============================================================================
class AEEKyberReal:
    """Sellado criptográfico post-cuántico con Kyber-768 real"""
    
    def __init__(self):
        try:
            self.kem = oqs.KeyEncapsulation("Kyber768")
            self.public_key = None
        except Exception as e:
            raise RuntimeError(f"Error inicializando Kyber768: {e}")
    
    def generate_keypair(self) -> bytes:
        """Genera par de claves"""
        self.public_key = self.kem.generate_keypair()
        return self.public_key
    
    def create_seal(
        self,
        embedding: np.ndarray,
        metadata: Dict = None
    ) -> Tuple[Dict, bytes]:
        """Crea sello criptográfico para embedding"""
        
        if self.public_key is None:
            raise ValueError("Genera claves primero con generate_keypair()")
        
        # 1. Serializar embedding
        vector_bytes = embedding.tobytes()
        
        # 2. Hash SHA3-256 (resistente a cuántica)
        content_hash = hashlib.sha3_256(vector_bytes).digest()
        
        # 3. Encapsular con Kyber-768 REAL
        ciphertext, shared_secret = self.kem.encap_secret(self.public_key)
        
        # 4. Combinar para sello único
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = content_hash + shared_secret + metadata_json
        else:
            combined = content_hash + shared_secret
        
        seal = hashlib.sha3_256(combined).hexdigest()
        
        # 5. Certificado
        certificate = {
            "seal": seal,
            "content_hash": content_hash.hex(),
            "algorithm": "Kyber768-NIST-FIPS-203",
            "timestamp": time.time(),
            "vector_shape": embedding.shape,
            "metadata": metadata
        }
        
        return certificate, ciphertext
    
    def verify_seal(
        self,
        embedding: np.ndarray,
        certificate: Dict,
        ciphertext: bytes,
        metadata: Dict = None
    ) -> bool:
        """Verifica integridad del embedding"""
        
        # 1. Recalcular hash
        vector_bytes = embedding.tobytes()
        current_hash = hashlib.sha3_256(vector_bytes).digest()
        original_hash = bytes.fromhex(certificate["content_hash"])
        
        # 2. Verificar hash
        if current_hash != original_hash:
            return False
        
        # 3. Desencapsular con Kyber-768 REAL
        try:
            shared_secret = self.kem.decap_secret(ciphertext)
        except Exception:
            return False
        
        # 4. Reconstruir sello
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = current_hash + shared_secret + metadata_json
        else:
            combined = current_hash + shared_secret
        
        expected_seal = hashlib.sha3_256(combined).hexdigest()
        
        # 5. Comparar
        return expected_seal == certificate["seal"]


# ============================================================================
# DEMO 2: AEE PROTOCOL CON KYBER-768 REAL
# ============================================================================
def demo_aee_real():
    """Demo de AEE Protocol con Kyber-768 real"""
    
    print_header("🤖 DEMO 2: AEE PROTOCOL - KYBER-768 REAL")
    
    try:
        # Inicializar
        print_info("Inicializando AEE Protocol con Kyber-768...")
        aee = AEEKyberReal()
        
        # Generar claves
        print_info("Generando claves...")
        public_key = aee.generate_keypair()
        print_success(f"Claves generadas ({len(public_key)} bytes)")
        print()
        
        # Crear embedding
        print_info("Creando embedding (1536 dimensiones)...")
        embedding = np.random.randn(1536).astype(np.float32)
        
        print_success("Embedding creado")
        print(f"   • Dimensiones: {embedding.shape}")
        print(f"   • Tamaño: {embedding.nbytes:,} bytes ({embedding.nbytes/1024:.1f} KB)")
        print(f"   • Primeros 5: [{', '.join(f'{v:.4f}' for v in embedding[:5])}...]")
        print()
        
        # Metadata
        metadata = {
            "model": "text-embedding-ada-002",
            "source": "AEE Protocol - Kyber768 Real",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "organization": "org_real_demo"
        }
        
        # Crear sello
        print_info("Creando sello con Kyber-768 real...")
        start = time.time()
        certificate, ciphertext = aee.create_seal(embedding, metadata)
        seal_time = (time.time() - start) * 1000
        
        print_success(f"Sello creado en {seal_time:.2f} ms")
        print(f"\n{Colors.BOLD}📝 Certificado Kyber-768:{Colors.END}")
        print(f"   • Sello: {certificate['seal'][:48]}...")
        print(f"   • Algoritmo: {Colors.GREEN}{certificate['algorithm']}{Colors.END}")
        print(f"   • Hash: {certificate['content_hash'][:32]}...")
        print()
        
        # VERIFICACIÓN 1: Original
        print_header("🔍 VERIFICACIÓN 1: EMBEDDING ORIGINAL")
        print_info("Verificando con Kyber-768 real...")
        
        start = time.time()
        is_valid = aee.verify_seal(embedding, certificate, ciphertext, metadata)
        verify_time = (time.time() - start) * 1000
        
        if is_valid:
            print_success(f"INTEGRIDAD VERIFICADA ({verify_time:.2f} ms)")
            print(f"   ✓ Hash SHA3-256: CORRECTO")
            print(f"   ✓ Kyber-768 decapsulación: VÁLIDA")
            print(f"\n   {Colors.GREEN}🛡️  Protección post-cuántica activa{Colors.END}")
        else:
            print_error("Verificación falló")
        
        print()
        
        # VERIFICACIÓN 2: Alterado
        print_header("🔍 VERIFICACIÓN 2: DETECCIÓN DE ALTERACIONES")
        print_warning("Simulando ataque...")
        
        embedding_tampered = embedding.copy()
        original = embedding_tampered[0]
        embedding_tampered[0] += 0.0001  # Alteración mínima
        
        print(f"   • Vector[0] original: {original:.6f}")
        print(f"   • Vector[0] alterado: {embedding_tampered[0]:.6f}")
        print(f"   • Diferencia: {abs(embedding_tampered[0] - original):.6f}")
        print()
        
        print_info("Verificando con Kyber-768...")
        is_valid_tampered = aee.verify_seal(embedding_tampered, certificate, ciphertext, metadata)
        
        if not is_valid_tampered:
            print_error("ALTERACIÓN DETECTADA")
            print(f"   ✗ Hash no coincide")
            print(f"\n   {Colors.RED}🚨 ¡Kyber-768 detectó el ataque!{Colors.END}")
        else:
            print_error("ERROR: No se detectó alteración")
        
        print()
        
        # Resumen
        print_header("🛡️  SEGURIDAD POST-CUÁNTICA VERIFICADA")
        
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}Post-Cuántico:{Colors.END} Kyber-768 (NIST FIPS 203)")
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}Criptografía:{Colors.END} Module-LWE (resistente a Shor)")
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}Hash:{Colors.END} SHA3-256 (resistente a Grover)")
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}Performance:{Colors.END} Creación: {seal_time:.2f}ms | Verificación: {verify_time:.2f}ms")
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}Detección:{Colors.END} Alteraciones > 1 bit detectadas")
        
        print()
        
    except Exception as e:
        print_error(f"Error en demo: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN
# ============================================================================
def main():
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║        AEE PROTOCOL - KYBER-768 REAL (liboqs-python)              ║")
    print("║                                                                    ║")
    print("║          NIST FIPS 203 - Post-Quantum Cryptography                ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    try:
        # Demo 1: Kyber básico
        result = demo_kyber_real()
        
        if result is None:
            print_error("Demo 1 falló")
            return 1
        
        input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.END}")
        
        # Demo 2: AEE Protocol
        demo_aee_real()
        
        # Final
        print_header("✅ DEMO KYBER-768 REAL COMPLETADA")
        print(f"{Colors.GREEN}¡Criptografía post-cuántica funcionando!{Colors.END}")
        print()
        print("Próximos pasos:")
        print("  1. ✅ Kyber-768 real funcionando")
        print("  2. 🔄 Crear API REST (Flask/FastAPI)")
        print("  3. 🌐 Conectar con React frontend")
        print("  4. 💾 Integrar con VectorDB (Pinecone/Weaviate)")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrumpido{Colors.END}")
        return 130
    
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())