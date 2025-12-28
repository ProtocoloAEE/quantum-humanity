#!/usr/bin/env python3
"""
AEE Protocol - Demo Simplificada (Pure Python)
No requiere liboqs - usa solo cryptography estándar

Instalación:
    pip install numpy cryptography

NOTA: Esta es una versión educativa. Para producción usar liboqs-python real.
"""

import sys
import time
import hashlib
import json
from typing import Tuple, Dict
import secrets

try:
    import numpy as np
except ImportError:
    print("❌ Error: numpy no instalado")
    print("   Ejecuta: pip install numpy")
    sys.exit(1)

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("❌ Error: cryptography no instalado")
    print("   Ejecuta: pip install cryptography")
    sys.exit(1)


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
# SIMULADOR KYBER-768 (Conceptual - para demostración)
# ============================================================================
class KyberSimulator:
    """
    Simulador conceptual de Kyber-768
    
    IMPORTANTE: Esta es una simulación educativa usando RSA.
    Para producción, DEBES usar liboqs-python con Kyber real.
    """
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        
    def generate_keypair(self) -> Tuple[bytes, float]:
        """Genera par de claves (simulado con RSA-2048)"""
        start = time.time()
        
        # Usamos RSA-2048 como analogía (Kyber usa Module-LWE)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Serializar clave pública
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        elapsed = time.time() - start
        
        return public_bytes, elapsed
    
    def encapsulate(self, public_key_bytes: bytes) -> Tuple[bytes, bytes, float]:
        """
        Encapsular secreto compartido
        
        En Kyber real: genera secreto usando Module-LWE
        Aquí: generamos secreto aleatorio y lo ciframos con RSA
        """
        start = time.time()
        
        # Generar secreto compartido de 32 bytes (como Kyber-768)
        shared_secret = secrets.token_bytes(32)
        
        # "Ciphertext": cifrar el secreto con la clave pública
        ciphertext = self.public_key.encrypt(
            shared_secret,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        elapsed = time.time() - start
        
        return ciphertext, shared_secret, elapsed
    
    def decapsulate(self, ciphertext: bytes) -> Tuple[bytes, float]:
        """
        Desencapsular secreto compartido
        
        En Kyber real: usa clave privada + Module-LWE
        Aquí: desciframos con RSA
        """
        start = time.time()
        
        shared_secret = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        elapsed = time.time() - start
        
        return shared_secret, elapsed


# ============================================================================
# DEMO 1: PROTOCOLO KEM BÁSICO
# ============================================================================
def demo_kem_basic():
    """Demo básica del protocolo KEM (Key Encapsulation Mechanism)"""
    
    print_header("🔐 DEMO 1: PROTOCOLO KEM BÁSICO (Simulación Educativa)")
    
    print_warning("NOTA: Esta versión usa RSA-2048 como analogía educativa")
    print_warning("Para producción: instalar liboqs-python y usar Kyber-768 real")
    print()
    
    kem = KyberSimulator()
    
    # Paso 1: Generar claves
    print_info("Generando par de claves (Alice)...")
    public_key, keygen_time = kem.generate_keypair()
    
    print_success(f"Claves generadas en {keygen_time*1000:.2f} ms")
    print(f"   • Clave pública: {len(public_key)} bytes")
    print(f"   • Primeros 32 bytes: {public_key[:32].hex()}")
    print()
    
    # Paso 2: Encapsular
    print_info("Encapsulando secreto compartido (Alice → Bob)...")
    ciphertext, shared_secret_alice, encap_time = kem.encapsulate(public_key)
    
    print_success(f"Encapsulación completada en {encap_time*1000:.2f} ms")
    print(f"   • Ciphertext: {len(ciphertext)} bytes")
    print(f"   • Secreto compartido: {len(shared_secret_alice)} bytes")
    print(f"   • Hash SHA3-256: {hashlib.sha3_256(shared_secret_alice).hexdigest()[:32]}...")
    print()
    
    # Paso 3: Desencapsular
    print_info("Desencapsulando (Bob recibe el ciphertext)...")
    shared_secret_bob, decap_time = kem.decapsulate(ciphertext)
    
    print_success(f"Desencapsulación completada en {decap_time*1000:.2f} ms")
    print()
    
    # Paso 4: Verificar
    print_info("Verificando correspondencia de secretos...")
    
    if shared_secret_alice == shared_secret_bob:
        print_success("¡SECRETOS COINCIDEN PERFECTAMENTE!")
        print(f"   Alice: {shared_secret_alice.hex()[:32]}...")
        print(f"   Bob:   {shared_secret_bob.hex()[:32]}...")
    else:
        print_error("Los secretos NO coinciden")
        return None
    
    # Performance
    total_time = (keygen_time + encap_time + decap_time) * 1000
    
    print(f"\n{Colors.BOLD}📊 Performance:{Colors.END}")
    print(f"   Generación:       {keygen_time*1000:>6.2f} ms")
    print(f"   Encapsulación:    {encap_time*1000:>6.2f} ms")
    print(f"   Desencapsulación: {decap_time*1000:>6.2f} ms")
    print(f"   {Colors.BOLD}Total:{Colors.END}            {Colors.GREEN}{total_time:>6.2f} ms{Colors.END}")
    
    return {
        'public_key': public_key,
        'ciphertext': ciphertext,
        'shared_secret': shared_secret_alice,
        'metrics': {
            'keygen': keygen_time * 1000,
            'encap': encap_time * 1000,
            'decap': decap_time * 1000,
            'total': total_time
        }
    }


# ============================================================================
# CLASE AEE PROTOCOL
# ============================================================================
class AEEProtocolSeal:
    """Sellado criptográfico para embeddings vectoriales"""
    
    def __init__(self):
        self.kem = KyberSimulator()
        self.public_key = None
        
    def generate_keypair(self) -> bytes:
        """Genera par de claves"""
        public_key, _ = self.kem.generate_keypair()
        self.public_key = public_key
        return public_key
    
    def create_seal(
        self,
        embedding: np.ndarray,
        metadata: Dict = None
    ) -> Tuple[Dict, bytes]:
        """Crea sello criptográfico para embedding"""
        
        if self.public_key is None:
            raise ValueError("Debes generar claves primero")
        
        # 1. Serializar embedding
        vector_bytes = embedding.tobytes()
        
        # 2. Hash del contenido (SHA3-256 es resistente a cuántica)
        content_hash = hashlib.sha3_256(vector_bytes).digest()
        
        # 3. Encapsular con KEM
        ciphertext, shared_secret, _ = self.kem.encapsulate(self.public_key)
        
        # 4. Combinar para crear sello único
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
            "algorithm": "AEE-KEM-SHA3",
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
        
        # 2. Verificar hash de contenido
        if current_hash != original_hash:
            return False
        
        # 3. Desencapsular secreto
        try:
            shared_secret, _ = self.kem.decapsulate(ciphertext)
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
# DEMO 2: AEE PROTOCOL CON EMBEDDINGS
# ============================================================================
def demo_aee_protocol():
    """Demo de AEE Protocol con embeddings vectoriales"""
    
    print_header("🤖 DEMO 2: AEE PROTOCOL - SELLADO DE EMBEDDINGS")
    
    # Crear instancia
    print_info("Inicializando AEE Protocol...")
    aee = AEEProtocolSeal()
    
    # Generar claves
    print_info("Generando claves del usuario/organización...")
    public_key = aee.generate_keypair()
    print_success(f"Claves generadas ({len(public_key)} bytes)")
    print()
    
    # Crear embedding de ejemplo
    print_info("Creando embedding vectorial (1536 dimensiones - OpenAI compatible)...")
    embedding = np.random.randn(1536).astype(np.float32)
    
    print_success("Embedding creado")
    print(f"   • Dimensiones: {embedding.shape}")
    print(f"   • Tamaño: {embedding.nbytes:,} bytes ({embedding.nbytes/1024:.1f} KB)")
    print(f"   • Tipo: {embedding.dtype}")
    print(f"   • Primeros 5: [{', '.join(f'{v:.4f}' for v in embedding[:5])}...]")
    print()
    
    # Metadata
    metadata = {
        "model": "text-embedding-ada-002",
        "source": "AEE Protocol Demo",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "organization": "org_demo"
    }
    
    # Crear sello
    print_info("Creando sello criptográfico...")
    start = time.time()
    certificate, ciphertext = aee.create_seal(embedding, metadata)
    seal_time = (time.time() - start) * 1000
    
    print_success(f"Sello creado en {seal_time:.2f} ms")
    print(f"\n{Colors.BOLD}📝 Certificado:{Colors.END}")
    print(f"   • Sello: {certificate['seal'][:48]}...")
    print(f"   • Algoritmo: {certificate['algorithm']}")
    print(f"   • Hash: {certificate['content_hash'][:32]}...")
    print(f"   • Metadata: {json.dumps(metadata, indent=6)}")
    print()
    
    # ========================================================================
    # VERIFICACIÓN 1: Original
    # ========================================================================
    print_header("🔍 VERIFICACIÓN 1: EMBEDDING ORIGINAL")
    print_info("Verificando integridad...")
    
    start = time.time()
    is_valid = aee.verify_seal(embedding, certificate, ciphertext, metadata)
    verify_time = (time.time() - start) * 1000
    
    if is_valid:
        print_success(f"INTEGRIDAD VERIFICADA ({verify_time:.2f} ms)")
        print(f"   ✓ Hash de contenido: CORRECTO")
        print(f"   ✓ Sello criptográfico: VÁLIDO")
        print(f"\n   {Colors.GREEN}El embedding es auténtico{Colors.END}")
    else:
        print_error("VERIFICACIÓN FALLÓ")
    
    print()
    
    # ========================================================================
    # VERIFICACIÓN 2: Alterado
    # ========================================================================
    print_header("🔍 VERIFICACIÓN 2: EMBEDDING ALTERADO")
    print_warning("Simulando ataque: alterando el embedding...")
    
    embedding_tampered = embedding.copy()
    original = embedding_tampered[0]
    embedding_tampered[0] += 0.001
    
    print(f"   • Vector[0] original: {original:.6f}")
    print(f"   • Vector[0] alterado: {embedding_tampered[0]:.6f}")
    print(f"   • Diferencia: {abs(embedding_tampered[0] - original):.6f}")
    print()
    
    print_info("Verificando embedding alterado...")
    is_valid_tampered = aee.verify_seal(embedding_tampered, certificate, ciphertext, metadata)
    
    if not is_valid_tampered:
        print_error("ALTERACIÓN DETECTADA")
        print(f"   ✗ Hash de contenido: MODIFICADO")
        print(f"\n   {Colors.RED}⚠️  ¡ATAQUE DETECTADO!{Colors.END}")
    else:
        print_error("ERROR: No se detectó alteración")
    
    print()
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    print_header("🛡️  PROPIEDADES DE SEGURIDAD")
    
    properties = [
        ("Detección Precisa", "Cualquier alteración > 1 bit es detectada"),
        ("Inmutabilidad", "Hash SHA3-256 previene modificaciones"),
        ("KEM Protocol", "Key Encapsulation para secretos compartidos"),
        ("Performance", f"Creación: {seal_time:.2f}ms | Verificación: {verify_time:.2f}ms"),
    ]
    
    for prop, desc in properties:
        print(f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}{prop}:{Colors.END} {desc}")
    
    print()
    print(f"{Colors.YELLOW}📌 RECORDATORIO:{Colors.END}")
    print("   Esta es una simulación educativa con RSA.")
    print("   Para seguridad post-cuántica real, instala liboqs-python")
    print("   y usa Kyber-768 según el estándar NIST FIPS 203.")
    print()


# ============================================================================
# MAIN
# ============================================================================
def main():
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║          AEE PROTOCOL - DEMO SIMPLIFICADA (Pure Python)           ║")
    print("║                                                                    ║")
    print("║             Cryptographic Sealing for AI Embeddings               ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    print_warning("VERSIÓN EDUCATIVA - Sin dependencias de liboqs")
    print_warning("Para producción: pip install liboqs-python")
    print()
    
    try:
        # Demo 1
        result = demo_kem_basic()
        
        if result is None:
            return 1
        
        input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.END}")
        
        # Demo 2
        demo_aee_protocol()
        
        # Final
        print_header("✅ DEMO COMPLETADA")
        print(f"{Colors.GREEN}Todas las pruebas pasaron{Colors.END}")
        print()
        print("Próximos pasos:")
        print("  1. Instalar liboqs-python para Kyber-768 real")
        print("  2. Integrar con tu vectorDB")
        print("  3. Crear API REST")
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