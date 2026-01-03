# -*- coding: utf-8 -*-
"""
# -*- coding: utf-8 -*-
"""
import sys
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import nacl.signing
import nacl.encoding

# Corrección de codificación para Windows para evitar errores en terminal.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

@dataclass
class DualSignature:
    """
    Almacena una firma dual que combina un algoritmo clásico (Ed25519) y uno
    post-cuántico (placeholder), junto con metadatos forenses cruciales.

    Attributes:
        hash (str): Hash SHA-256 de la evidencia original.
        classic_signature (str): Firma digital Ed25519 del hash.
        pqc_signature (str): Placeholder para la futura firma PQC.
        timestamp (str): Marca de tiempo en formato ISO 8601 UTC.
        algorithm (str): Descripción del stack de algoritmos utilizados.
    """
    hash: str
    classic_signature: str
    pqc_signature: str
    timestamp: str
    algorithm: str

    def to_dict(self) -> dict:
        """Convierte la instancia de la clase en un diccionario."""
        return asdict(self)

class HybridCryptoEngine:
    """
    Motor criptográfico responsable de generar y verificar las firmas duales.
    Utiliza PyNaCl para la criptografía de curva elíptica (Ed25519).
    """
    def __init__(self):
        """
        Inicializa el motor generando una nueva clave de firma Ed25519.
        En un entorno de producción, esta clave debería ser cargada desde
        un almacén seguro (HSM, gestor de secretos, etc.).
        """
        self._signing_key: nacl.signing.SigningKey = nacl.signing.SigningKey.generate()
        self.verify_key: nacl.signing.VerifyKey = self._signing_key.verify_key
        self.verify_key_hex: str = self.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')

    def sign_evidence(self, data: bytes) -> DualSignature:
        """
        Procesa y firma digitalmente una pieza de evidencia.

        El proceso sigue los siguientes pasos:
        1. Calcula el hash SHA-256 de los datos de entrada.
        2. Firma el hash resultante con la clave privada Ed25519.
        3. Genera una capa de integridad adicional con SHA3-256 sobre la firma clásica.
           Este no es un algoritmo PQC, sino un sellado adicional.
        4. Empaqueta los resultados en un objeto DualSignature.

        Args:
            data: La evidencia digital en formato de bytes.

        Returns:
            Una instancia de DualSignature con los resultados criptográficos.
        """
        # 1. Calcular Hash SHA-256
        evidence_hash = hashlib.sha256(data).hexdigest()

        # 2. Firmar el hash con Ed25519
        signed_hash = self._signing_key.sign(evidence_hash.encode('utf-8'))
        classic_sig_hex = signed_hash.signature.hex()

        # 3. Generar capa de integridad SHA-3 (como placeholder de PQC)
        # NOTA: Esto NO es una firma PQC, es un hash de la firma clásica
        # para agregar una capa de complejidad y demostrar el concepto.
        pqc_placeholder = hashlib.sha3_256(classic_sig_hex.encode('utf-8')).hexdigest()

        return DualSignature(
            hash=evidence_hash,
            classic_signature=classic_sig_hex,
            pqc_signature=f"sha3-256({pqc_placeholder})",
            timestamp=datetime.now(timezone.utc).isoformat(),
            algorithm="Ed25519_SHA256+SHA3-256"
        )

    def verify_signature(self, signature: DualSignature, original_data: bytes) -> bool:
        """
        Verifica la integridad de una evidencia contrastándola con su firma.

        Args:
            signature: El objeto DualSignature a verificar.
            original_data: Los datos originales de la evidencia.

        Returns:
            True si la firma es válida y el hash coincide, False en caso contrario.
        """
        # Recalcular el hash de la data original
        recalculated_hash = hashlib.sha256(original_data).hexdigest()

        # Comparar hashes
        if recalculated_hash != signature.hash:
            return False

        # Verificar la firma Ed25519
        try:
            verify_key = nacl.signing.VerifyKey(signature.classic_signature, encoder=nacl.encoding.HexEncoder)
            verify_key.verify(recalculated_hash.encode('utf-8'))
            return True
        except Exception:
            # La firma es inválida
            return False

# Ejemplo de uso (opcional, para testing)
if __name__ == '__main__':
    engine = HybridCryptoEngine()
    print(f"🔑 Clave de Verificación (Pública): {engine.verify_key_hex}")

    # Simular evidencia
    test_evidence = b"Esta es una prueba de evidencia digital para el protocolo AEE."
    
    # Firmar evidencia
    digital_certificate = engine.sign_evidence(test_evidence)
    print("\n--- Certificado Generado ---")
    print(digital_certificate.to_dict())

    # Verificar integridad (caso exitoso)
    is_valid_ok = engine.verify_signature(digital_certificate, test_evidence)
    print(f"\n✅ Verificación (datos correctos): {'VÁLIDA' if is_valid_ok else 'INVÁLIDA'}")

    # Verificar integridad (caso fallido)
    tampered_evidence = b"Esta es una prueba de evidencia digital ALTERADA."
    is_valid_fail = engine.verify_signature(digital_certificate, tampered_evidence)
    print(f"❌ Verificación (datos alterados): {'VÁLIDA' if is_valid_fail else 'INVÁLIDA'}")
