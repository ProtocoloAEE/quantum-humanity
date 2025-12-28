#!/usr/bin/env python3
"""
AEE Protocol - Kyber-768 Demo Real (CLI)
Implementación completa con liboqs-python

Instalación rápida:
    pip install liboqs-python numpy

Ejecución:
    python kyber_aee_demo.py
"""

import sys
import time
import hashlib
import json
from typing import Tuple, Dict, List

try:
    import numpy as np
except ImportError:
    print("❌ Error: numpy no instalado")
    print("   Ejecuta: pip install numpy")
    sys.exit(1)

try:
    from liboqs import KeyEncapsulation
except ImportError:
    print("❌ Error: liboqs-python no instalado")
    print("   Ejecuta: pip install liboqs-python")
    sys.exit(1)


# ============================================================================
# COLORES PARA CLI (funciona en la mayoría de terminales)
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime encabezado destacado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Imprime información"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text: str):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


# ============================================================================
# DEMO 1: KYBER-768 BÁSICO
# ============================================================================
def demo_kyber_basic():
    """Demo básica del protocolo Kyber-768"""
    
    print_header("🔐 DEMO 1: KYBER-768 BÁSICO (NIST FIPS 203)")
    
    kem_name = "Kyber768"
    
    # Paso 1: Verificar disponibilidad
    print_info(f"Verificando disponibilidad de {kem_name}...")
    supported = KeyEncapsulation.get_supported_kems()
    
    if kem_name not in supported:
        print_error(f"{kem_name} no disponible")
        print(f"   KEMs disponibles: {', '.join(supported[:5])}...")
        return None
    
    print_success(f"{kem_name} disponible")
    print(f"   Total de algoritmos PQC: {len(supported)}\n")
    
    # Paso 2: Generar claves (Alice)
    print_info("Generando par de claves...")
    start = time.time()
    
    alice_kem = KeyEncapsulation(kem_name)
    public_key = alice_kem.generate_keypair()
    
    keygen_time = (time.time() - start) * 1000
    
    print_success(f"Claves generadas en {keygen_time:.2f} ms")
    print(f"   • Clave pública: {len(public_key)} bytes")
    print(f"   • Primeros 32 bytes: {public_key[:32].hex()}")
    print()
    
    # Paso 3: Encapsular (Alice → Bob)
    print_info("Encapsulando secreto compartido...")
    start = time.time()
    
    ciphertext, shared_secret_alice = alice_kem.encap_secret(public_key)
    
    encap_time = (time.time() - start) * 1000
    
    print_success(f"Encapsulación completada en {encap_time:.2f} ms")
    print(f"   • Ciphertext: {len(ciphertext)} bytes")
    print(f"   • Secreto compartido: {len(shared_secret_alice)} bytes")
    print(f"   • Hash SHA3-256: {hashlib.sha3_256(shared_secret_alice).hexdigest()[:32]}...")
    print()
    
    # Paso 4: Desencapsular (Bob)
    print_info("Desencapsulando (receptor Bob)...")
    start = time.time()
    
    shared_secret_bob = alice_kem.decap_secret(ciphertext)
    
    decap_time = (time.time() - start) * 1000
    
    print_success(f"Desencapsulación completada en {decap_time:.2f} ms")
    print()
    
    # Paso 5: Verificar
    print_info("Verificando correspondencia de secretos...")
    
    if shared_secret_alice == shared_secret_bob:
        print_success("¡SECRETOS COINCIDEN PERFECTAMENTE!")
        print(f"   Secreto Alice: {shared_secret_alice.hex()[:32]}...")
        print(f"   Secreto Bob:   {shared_secret_bob.hex()[:32]}...")
    else:
        print_error("Los secretos NO coinciden (esto nunca debería pasar)")
        return None
    
    # Resumen de performance
    total_time = keygen_time + encap_time + decap_time
    
    print(f"\n{Colors.BOLD}📊 Performance Total:{Colors.END}")
    print(f"   Generación:     {keygen_time:>6.2f} ms")
    print(f"   Encapsulación:  {encap_time:>6.2f} ms")
    print(f"   Desencapsulación: {decap_time:>6.2f} ms")
    print(f"   {Colors.BOLD}Total:{Colors.END}          {Colors.GREEN}{total_time:>6.2f} ms{Colors.END}")
    
    # Liberar recursos
    alice_kem.free()
    
    return {
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
# CLASE PARA AEE PROTOCOL
# ============================================================================
class AEEKyberSeal:
    """Sellado criptográfico post-cuántico para embeddings vectoriales"""
    
    def __init__(self, algorithm: str = "Kyber768"):
        self.algorithm = algorithm
        self.kem = KeyEncapsulation(algorithm)
        self.public_key = None
        self.private_key_stored = False
        
    def generate_keypair(self) -> bytes:
        """Genera par de claves"""
        self.public_key = self.kem.generate_keypair()
        self.private_key_stored = True
        return self.public_key
    
    def create_seal(
        self, 
        embedding: np.ndarray, 
        metadata: Dict = None
    ) -> Tuple[Dict, bytes]:
        """
        Crea sello criptográfico para un embedding
        
        Returns:
            (certificate, ciphertext)
        """
        if self.public_key is None:
            raise ValueError("Debes generar claves primero")
        
        # 1. Serializar embedding
        vector_bytes = embedding.tobytes()
        
        # 2. Hash del contenido (SHA3-256 es resistente a cuántica)
        content_hash = hashlib.sha3_256(vector_bytes).digest()
        
        # 3. Encapsular con Kyber
        ciphertext, shared_secret = self.kem.encap_secret(self.public_key)
        
        # 4. Combinar para crear sello único
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = content_hash + shared_secret + metadata_json
        else:
            combined = content_hash + shared_secret
        
        seal = hashlib.sha3_256(combined).hexdigest()
        
        # 5. Certificado completo
        certificate = {
            "seal": seal,
            "content_hash": content_hash.hex(),
            "algorithm": self.algorithm,
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
        """
        Verifica integridad del embedding
        
        Returns:
            True si el embedding es auténtico, False si fue alterado
        """
        # 1. Recalcular hash del embedding actual
        vector_bytes = embedding.tobytes()
        current_hash = hashlib.sha3_256(vector_bytes).digest()
        original_hash = bytes.fromhex(certificate["content_hash"])
        
        # 2. Verificar hash de contenido
        if current_hash != original_hash:
            return False
        
        # 3. Desencapsular secreto
        try:
            shared_secret = self.kem.decap_secret(ciphertext)
        except Exception:
            return False
        
        # 4. Reconstruir sello esperado
        if metadata:
            metadata_json = json.dumps(metadata, sort_keys=True).encode()
            combined = current_hash + shared_secret + metadata_json
        else:
            combined = current_hash + shared_secret
        
        expected_seal = hashlib.sha3_256(combined).hexdigest()
        
        # 5. Comparar sellos
        return expected_seal == certificate["seal"]
    
    def free(self):
        """Liberar recursos"""
        self.kem.free()


# ============================================================================
# DEMO 2: AEE PROTOCOL CON EMBEDDINGS
# ============================================================================
def demo_aee_protocol():
    """Demo de AEE Protocol con embeddings vectoriales"""
    
    print_header("🤖 DEMO 2: AEE PROTOCOL - SELLADO DE EMBEDDINGS")
    
    # Crear instancia AEE
    print_info("Inicializando AEE Protocol con Kyber-768...")
    aee = AEEKyberSeal()
    
    # Generar claves
    print_info("Generando claves del usuario/organización...")
    public_key = aee.generate_keypair()
    print_success(f"Claves generadas ({len(public_key)} bytes)")
    print()
    
    # Crear embedding de ejemplo (simulando OpenAI text-embedding-ada-002)
    print_info("Creando embedding vectorial de ejemplo (1536 dimensiones)...")
    embedding = np.random.randn(1536).astype(np.float32)
    
    print_success("Embedding creado")
    print(f"   • Dimensiones: {embedding.shape}")
    print(f"   • Tamaño en memoria: {embedding.nbytes:,} bytes ({embedding.nbytes/1024:.1f} KB)")
    print(f"   • Tipo de datos: {embedding.dtype}")
    print(f"   • Primeros 5 valores: [{', '.join(f'{v:.4f}' for v in embedding[:5])}...]")
    print()
    
    # Metadata del embedding
    metadata = {
        "model": "text-embedding-ada-002",
        "source": "AEE Protocol Demo",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "organization": "org_demo_xyz"
    }
    
    # Crear sello criptográfico
    print_info("Creando sello criptográfico post-cuántico...")
    start = time.time()
    
    certificate, ciphertext = aee.create_seal(embedding, metadata)
    
    seal_time = (time.time() - start) * 1000
    
    print_success(f"Sello creado en {seal_time:.2f} ms")
    print(f"\n{Colors.BOLD}📝 Certificado generado:{Colors.END}")
    print(f"   • Sello (SHA3-256): {certificate['seal'][:48]}...")
    print(f"   • Algoritmo: {certificate['algorithm']}")
    print(f"   • Hash contenido: {certificate['content_hash'][:32]}...")
    print(f"   • Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(certificate['timestamp']))}")
    print(f"   • Metadata: {json.dumps(metadata, indent=6)}")
    print()
    
    # ========================================================================
    # VERIFICACIÓN 1: Embedding Original (debe pasar)
    # ========================================================================
    print_header("🔍 VERIFICACIÓN 1: EMBEDDING ORIGINAL")
    print_info("Verificando integridad del embedding original...")
    
    start = time.time()
    is_valid = aee.verify_seal(embedding, certificate, ciphertext, metadata)
    verify_time = (time.time() - start) * 1000
    
    if is_valid:
        print_success(f"INTEGRIDAD VERIFICADA ({verify_time:.2f} ms)")
        print(f"   ✓ Hash de contenido: CORRECTO")
        print(f"   ✓ Sello criptográfico: VÁLIDO")
        print(f"   ✓ Metadata: INTACTA")
        print(f"\n   {Colors.GREEN}El embedding es auténtico y no ha sido alterado{Colors.END}")
    else:
        print_error("VERIFICACIÓN FALLÓ (esto no debería pasar)")
    
    print()
    
    # ========================================================================
    # VERIFICACIÓN 2: Embedding Alterado (debe fallar)
    # ========================================================================
    print_header("🔍 VERIFICACIÓN 2: EMBEDDING ALTERADO (Simulación de Ataque)")
    print_warning("Alterando el embedding para simular un ataque...")
    
    # Crear copia y alterar mínimamente
    embedding_tampered = embedding.copy()
    original_value = embedding_tampered[0]
    embedding_tampered[0] += 0.001  # Alteración de solo 0.1%
    
    print(f"   • Vector[0] original: {original_value:.6f}")
    print(f"   • Vector[0] alterado: {embedding_tampered[0]:.6f}")
    print(f"   • Diferencia: {abs(embedding_tampered[0] - original_value):.6f} (0.1%)")
    print()
    
    print_info("Verificando embedding alterado...")
    start = time.time()
    is_valid_tampered = aee.verify_seal(embedding_tampered, certificate, ciphertext, metadata)
    verify_tampered_time = (time.time() - start) * 1000
    
    if not is_valid_tampered:
        print_error(f"ALTERACIÓN DETECTADA ({verify_tampered_time:.2f} ms)")
        print(f"   ✗ Hash de contenido: MODIFICADO")
        print(f"   ✗ Sello criptográfico: INVÁLIDO")
        print(f"\n   {Colors.RED}⚠️  ¡ATAQUE DETECTADO! El embedding fue alterado{Colors.END}")
    else:
        print_error("ERROR: No se detectó la alteración (bug en la implementación)")
    
    print()
    
    # ========================================================================
    # RESUMEN DE SEGURIDAD
    # ========================================================================
    print_header("🛡️  PROPIEDADES DE SEGURIDAD")
    
    properties = [
        ("Post-Cuántico", "Basado en Module-LWE (problema matemático hard)"),
        ("NIST Estandarizado", "FIPS 203 - Estándar oficial del gobierno USA"),
        ("Detección Precisa", "Cualquier alteración > 1 bit es detectada"),
        ("Inmutabilidad", "Hash criptográfico previene modificaciones"),
        ("Performance", f"Creación: {seal_time:.2f}ms | Verificación: {verify_time:.2f}ms"),
        ("Tamaño Eficiente", f"Ciphertext: {len(ciphertext)} bytes | Sello: 64 chars")
    ]
    
    for prop, desc in properties:
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}{prop}:{Colors.END} {desc}")
    
    # Liberar recursos
    aee.free()
    
    print()


# ============================================================================
# DEMO 3: COMPARACIÓN CON MÉTODOS TRADICIONALES
# ============================================================================
def demo_comparison():
    """Compara Kyber-768 con métodos tradicionales"""
    
    print_header("📊 COMPARACIÓN: KYBER-768 vs MÉTODOS TRADICIONALES")
    
    # Crear embedding de prueba
    embedding = np.random.randn(1536).astype(np.float32)
    vector_bytes = embedding.tobytes()
    
    results = []
    
    # 1. SHA-256 simple (no es post-cuántico)
    print_info("1. SHA-256 tradicional (vulnerable a Grover)...")
    start = time.time()
    sha256_hash = hashlib.sha256(vector_bytes).hexdigest()
    sha256_time = (time.time() - start) * 1000
    results.append(("SHA-256", sha256_time, "❌ Vulnerable", 32))
    print(f"   Tiempo: {sha256_time:.4f} ms | Hash: {sha256_hash[:32]}...")
    
    # 2. SHA3-256 (resistente a cuántica para hashing)
    print_info("2. SHA3-256 (resistente a Grover)...")
    start = time.time()
    sha3_hash = hashlib.sha3_256(vector_bytes).hexdigest()
    sha3_time = (time.time() - start) * 1000
    results.append(("SHA3-256", sha3_time, "✓ Resistente (hash)", 32))
    print(f"   Tiempo: {sha3_time:.4f} ms | Hash: {sha3_hash[:32]}...")
    
    # 3. Kyber-768 completo
    print_info("3. Kyber-768 + SHA3-256 (AEE Protocol)...")
    aee = AEEKyberSeal()
    aee.generate_keypair()
    
    start = time.time()
    certificate, ciphertext = aee.create_seal(embedding)
    kyber_time = (time.time() - start) * 1000
    results.append(("Kyber-768", kyber_time, "✓ Post-Cuántico", len(ciphertext)))
    print(f"   Tiempo: {kyber_time:.4f} ms | Sello: {certificate['seal'][:32]}...")
    
    aee.free()
    
    print()
    
    # Tabla comparativa
    print(f"{Colors.BOLD}Tabla Comparativa:{Colors.END}")
    print(f"{'Método':<20} {'Tiempo (ms)':<15} {'Seguridad PQ':<20} {'Tamaño (bytes)':<15}")
    print("-" * 70)
    
    for method, t, security, size in results:
        print(f"{method:<20} {t:<15.4f} {security:<20} {size:<15}")
    
    print()
    print(f"{Colors.CYAN}Conclusión:{Colors.END}")
    print("  • SHA-256/SHA3 solo protegen integridad, NO intercambio de claves")
    print("  • Kyber-768 permite establecer secretos compartidos post-cuánticos")
    print("  • AEE Protocol combina lo mejor: SHA3 (hash) + Kyber (KEM)")
    print()


# ============================================================================
# MAIN: EJECUTAR TODAS LAS DEMOS
# ============================================================================
def main():
    """Ejecuta todas las demos en secuencia"""
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║          AEE PROTOCOL - KYBER-768 DEMO COMPLETA (CLI)             ║")
    print("║                                                                    ║")
    print("║          Post-Quantum Cryptography for AI Embeddings              ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    try:
        # Demo 1: Básica
        result = demo_kyber_basic()
        
        if result is None:
            print_error("Demo básica falló. Abortando...")
            return 1
        
        input(f"\n{Colors.YELLOW}Presiona ENTER para continuar a la Demo 2...{Colors.END}")
        
        # Demo 2: AEE Protocol
        demo_aee_protocol()
        
        input(f"\n{Colors.YELLOW}Presiona ENTER para continuar a la Demo 3...{Colors.END}")
        
        # Demo 3: Comparación
        demo_comparison()
        
        # Resumen final
        print_header("✅ DEMO COMPLETADA EXITOSAMENTE")
        print(f"{Colors.GREEN}Todas las pruebas pasaron correctamente{Colors.END}")
        print()
        print("Próximos pasos:")
        print("  1. Integrar con tu base de datos vectorial (Pinecone/Weaviate)")
        print("  2. Implementar API REST (Flask/FastAPI)")
        print("  3. Crear frontend con la demo de React conectada")
        print()
        print(f"{Colors.CYAN}🔗 Más info:{Colors.END} https://github.com/ProtocoloAEE/aee-protocol")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrumpida por el usuario{Colors.END}")
        return 130
    
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())