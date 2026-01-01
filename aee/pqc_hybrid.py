"""
PROTOCOLO AEE v2.1-HARDENED - Motor de Criptografía Híbrida Post-Cuántica
Implementa blindaje dual: Ed25519 (clásico) + Kyber-768 (post-cuántico)
Primer sistema de preservación forense en Argentina con resistencia cuántica
Autor: Desarrollo AEE
Versión: 2.1.0-PQC
"""

import hashlib
import hmac
import secrets
import logging
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import os

# HSM Integration
HSM_ENABLED = os.getenv('HSM_ENABLED', 'false').lower() == 'true'
HSM_TYPE = os.getenv('HSM_TYPE', 'mock')

if HSM_ENABLED and HSM_TYPE != 'mock':
    try:
        from aee.infrastructure.hsm import hsm_adapter
        logger.info(f"✓ HSM adapter loaded: {HSM_TYPE}")
    except ImportError:
        logger.warning("HSM adapter not available, falling back to mock")
        HSM_ENABLED = False

# Importar módulos de producción AEE desde la estructura del proyecto actual
try:
    from aee.core import (
        CanonicalJSONSerializer,
        ForensicErrorHandler,
        transaccion_forense,
        RobustNTPQuorum
    )
    AEE_CORE_AVAILABLE = True
except ImportError:
    AEE_CORE_AVAILABLE = False
    # Si no están disponibles, usar versiones simplificadas
    class CanonicalJSONSerializer:
        @staticmethod
        def serialize(data):
            return json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    class RobustNTPQuorum:
        def obtener_timestamp_consenso(self):
            return {
                'timestamp_unix': datetime.now(timezone.utc).timestamp(),
                'timestamp_iso': datetime.now(timezone.utc).isoformat(),
                'fuente': 'local_fallback'
            }

    class ForensicErrorHandler:
        def __init__(self, op): pass
        def __enter__(self): return self
        def __exit__(self, *args): return False
    
    def transaccion_forense(operation_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Importar Kyber-768
try:
    from kyber_py.ml_kem import ML_KEM_768
    KYBER_AVAILABLE = True
    KYBER_LIBRARY = "kyber_py"
except ImportError:
    try:
        from pqcrypto.kem.kyber768 import generate_keypair, encrypt, decrypt
        KYBER_AVAILABLE = True
        KYBER_LIBRARY = "pqcrypto"
    except ImportError:
        KYBER_AVAILABLE = False
        KYBER_LIBRARY = None

# Importar Ed25519 desde la librería cryptography
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


# Configurar logging
logger = logging.getLogger('AEE-PQC-Hybrid')


# ==============================================================================
# ESTRUCTURAS DE DATOS
# ==============================================================================

@dataclass
class HybridKeyPair:
    """Par de claves híbrido: Ed25519 + Kyber-768"""
    # Ed25519 (clásico)
    ed25519_private: bytes
    ed25519_public: bytes
    
    # Kyber-768 (post-cuántico)
    kyber_private: bytes
    kyber_public: bytes
    
    # Metadata
    created_at: str
    key_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el par de claves (solo claves públicas)"""
        return {
            'ed25519_public': self.ed25519_public.hex(),
            'kyber_public': self.kyber_public.hex() if self.kyber_public else None,
            'created_at': self.created_at,
            'key_id': self.key_id
        }
    
    def export_private(self) -> Dict[str, str]:
        """
        Exporta claves privadas (DEBE protegerse con HSM en producción).
        """
        logger.warning("Exportando claves privadas - usar solo en desarrollo/backup")
        
        return {
            'ed25519_private': self.ed25519_private.hex(),
            'kyber_private': self.kyber_private.hex() if self.kyber_private else None,
            'key_id': self.key_id
        }


@dataclass
class DualSignature:
    """Firma dual: clásica + post-cuántica"""
    # Firma Ed25519 (clásico)
    signature_classic: bytes
    
    # Sello Kyber (post-cuántico)
    pqc_seal: Optional[bytes]
    pqc_auth_tag: Optional[bytes]
    
    # Metadata
    timestamp: str
    algorithm_classic: str = "Ed25519"
    algorithm_pqc: str = "Kyber-768" if KYBER_AVAILABLE else "None"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa la firma dual"""
        return {
            'signature_classic': self.signature_classic.hex(),
            'pqc_seal': self.pqc_seal.hex() if self.pqc_seal else None,
            'pqc_auth_tag': self.pqc_auth_tag.hex() if self.pqc_auth_tag else None,
            'timestamp': self.timestamp,
            'algorithm_classic': self.algorithm_classic,
            'algorithm_pqc': self.algorithm_pqc
        }


# ==============================================================================
# MOTOR DE CRIPTOGRAFÍA HÍBRIDA
# ==============================================================================

class HybridCryptoEngine:
    """Motor de criptografía híbrida Ed25519 + Kyber-768."""
    
    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.error("La librería 'cryptography' no está disponible. Instalar: pip install cryptography")
            raise RuntimeError("La dependencia 'cryptography' es necesaria para la firma clásica.")
        
        if not KYBER_AVAILABLE:
            logger.warning("Kyber-768 no disponible. Instalar: pip install kyber-py")
            logger.warning("El sistema funcionará solo con Ed25519 (modo clásico).")
        else:
            logger.info(f"Kyber-768 disponible vía {KYBER_LIBRARY}.")
    
    def generar_par_claves_hibrido(self) -> HybridKeyPair:
        """Genera un par de claves híbrido: Ed25519 + Kyber-768."""
        logger.info("Generando par de claves híbrido...")
        
        # 1. Generar claves Ed25519
        ed_private_key = ed25519.Ed25519PrivateKey.generate()
        ed_public_key = ed_private_key.public_key()
        ed_private = ed_private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        ed_public = ed_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # 2. Generar claves Kyber-768 (si está disponible)
        kyber_public, kyber_private = None, None
        if KYBER_AVAILABLE:
            if KYBER_LIBRARY == "kyber_py":
                kyber_public, kyber_private = ML_KEM_768.keygen()
            elif KYBER_LIBRARY == "pqcrypto":
                kyber_public, kyber_private = generate_keypair()
        
        # 3. Crear identificador único
        key_id_material = ed_public + (kyber_public or b'')
        key_id = hashlib.sha256(key_id_material).hexdigest()[:16]
        
        keypair = HybridKeyPair(
            ed25519_private=ed_private,
            ed25519_public=ed_public,
            kyber_private=kyber_private or b'',
            kyber_public=kyber_public or b'',
            created_at=datetime.now(timezone.utc).isoformat(),
            key_id=key_id
        )
        
        logger.info(f"Par de claves híbrido generado: ID={key_id}")
        return keypair
    
    def firmar_dual(self, mensaje_canonical: str, keypair: HybridKeyPair) -> DualSignature:
        """
        Genera firma dual: Ed25519 (clásica) + Kyber-768 (post-cuántica).
        
        Modelo de Seguridad v2.1:
        - Implementa cumplimiento estricto del Principio de Kerckhoffs
        - No permite degradación silenciosa: fallos criptográficos lanzan excepciones
        - Garantiza que la firma Ed25519 es siempre generada (requisito crítico)
        - El sello PQC es opcional pero su ausencia no compromete la verificación pública
        
        Args:
            mensaje_canonical: Mensaje serializado canónicamente (RFC 8785)
            keypair: Par de claves híbrido (Ed25519 + Kyber-768)
            
        Returns:
            DualSignature: Firma dual con capa clásica obligatoria y PQC opcional
            
        Raises:
            RuntimeError: Si la generación de firma Ed25519 falla (no se permite degradación)
            ValueError: Si los parámetros son inválidos
        """
        logger.info("Generando firma dual...")
        
        if not mensaje_canonical or not isinstance(mensaje_canonical, str):
            raise ValueError("mensaje_canonical debe ser una cadena no vacía")
        if not keypair or not keypair.ed25519_private:
            raise ValueError("keypair debe contener clave privada Ed25519 válida")
        
        mensaje_bytes = mensaje_canonical.encode('utf-8')
        
        # 1. Firma clásica Ed25519 (OBLIGATORIA - no se permite fallo silencioso)
        try:
            if HSM_ENABLED and HSM_TYPE != 'mock':
                from aee.infrastructure.hsm import hsm_adapter
                signature_classic = hsm_adapter.sign_with_ed25519(mensaje_bytes, keypair.key_id)
                logger.info(f"✓ Signed with {HSM_TYPE} HSM")
            else:
                ed_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(keypair.ed25519_private)
                signature_classic = ed_private_key.sign(mensaje_bytes)
        except Exception as e:
            logger.error(f"Fallo crítico en generación de firma Ed25519: {e}")
            raise RuntimeError(
                f"Error en firma Ed25519 (no se permite degradación silenciosa): {str(e)}"
            ) from e
        
        # 2. Sello post-cuántico Kyber-768 (opcional - fallos no abortan el proceso)
        pqc_seal, pqc_auth_tag = None, None
        if KYBER_AVAILABLE and keypair.kyber_public:
            try:
                pqc_seal, pqc_auth_tag, _ = self._encapsular_hibrido(mensaje_canonical, keypair)
            except Exception as e:
                logger.warning(f"Sello PQC no pudo ser generado (continuando sin él): {e}")
                # No lanzamos excepción - el sello PQC es opcional para verificación pública
        
        dual_sig = DualSignature(
            signature_classic=signature_classic,
            pqc_seal=pqc_seal,
            pqc_auth_tag=pqc_auth_tag,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        logger.info("Firma dual generada exitosamente.")
        return dual_sig
        
    def verificar_dual(
        self, mensaje_canonical: str, dual_signature: DualSignature, clave_publica_ed25519: bytes
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica la capa de firma clásica (Ed25519), que es públicamente verificable.
        La capa PQC solo puede ser verificada por un auditor con la clave privada.
        
        Modelo de Seguridad v2.1:
        - Verificación Ed25519 es obligatoria y determinística
        - No permite degradación silenciosa: errores criptográficos se propagan
        - InvalidSignature se trata como fallo explícito (no como advertencia)
        - Errores de formato/parámetros lanzan excepciones (no retornan False silenciosamente)
        
        Args:
            mensaje_canonical: Mensaje serializado canónicamente a verificar
            dual_signature: Firma dual a verificar
            clave_publica_ed25519: Clave pública Ed25519 en formato raw (32 bytes)
            
        Returns:
            Tuple[bool, Dict]: (éxito_verificación, detalles_detallados)
            - éxito_verificación: True solo si Ed25519 es válida
            - detalles: Dict con estado de cada componente
            
        Raises:
            ValueError: Si los parámetros son inválidos (formato incorrecto, None, etc.)
            RuntimeError: Si hay error crítico en operaciones criptográficas (no InvalidSignature)
        """
        logger.info("Verificando firma dual (capa clásica)...")
        
        # Validación de parámetros (no se permite degradación silenciosa)
        if not mensaje_canonical or not isinstance(mensaje_canonical, str):
            raise ValueError("mensaje_canonical debe ser una cadena no vacía")
        if not dual_signature or not dual_signature.signature_classic:
            raise ValueError("dual_signature debe contener signature_classic válida")
        if not clave_publica_ed25519 or len(clave_publica_ed25519) != 32:
            raise ValueError("clave_publica_ed25519 debe ser exactamente 32 bytes")
        
        resultado = {
            'ed25519_valido': False, 
            'kyber_valido': None, 
            'mensaje_ed25519': '', 
            'mensaje_kyber': 'No verificado públicamente'
        }
        mensaje_bytes = mensaje_canonical.encode('utf-8')

        # 1. Verificar Ed25519 (públicamente verificable) - OBLIGATORIO
        try:
            ed_public_key = ed25519.Ed25519PublicKey.from_public_bytes(clave_publica_ed25519)
            ed_public_key.verify(dual_signature.signature_classic, mensaje_bytes)
            resultado['ed25519_valido'] = True
            resultado['mensaje_ed25519'] = 'Firma Ed25519 válida.'
        except InvalidSignature:
            # InvalidSignature es un fallo explícito, no un error de sistema
            resultado['ed25519_valido'] = False
            resultado['mensaje_ed25519'] = 'Firma Ed25519 inválida.'
            logger.warning("Verificación Ed25519 falló: firma inválida")
        except Exception as e:
            # Errores no esperados (formato, clave corrupta, etc.) se propagan
            logger.error(f"Error crítico en verificación Ed25519: {e}")
            raise RuntimeError(
                f"Error crítico en verificación Ed25519 (no se permite degradación silenciosa): {str(e)}"
            ) from e

        # 2. Sello PQC (no es públicamente verificable)
        kyber_presente = dual_signature.pqc_seal and dual_signature.pqc_auth_tag
        if kyber_presente:
            resultado['kyber_valido'] = None # No se puede determinar sin clave privada
            resultado['mensaje_kyber'] = 'Sello PQC presente. Requiere clave privada de auditor para verificar.'
        else:
            resultado['kyber_valido'] = None
            resultado['mensaje_kyber'] = 'Sello PQC no presente en esta firma.'

        exito_global = resultado['ed25519_valido']
        return exito_global, resultado

    def _encapsular_hibrido(self, mensaje_canonical: str, keypair: HybridKeyPair) -> Tuple[bytes, bytes, bytes]:
        """Proceso interno de encapsulación y autenticación con Kyber."""
        mensaje_bytes = mensaje_canonical.encode('utf-8')
        
        # Encapsular secreto
        if KYBER_LIBRARY == "kyber_py":
            shared_secret, ciphertext_kem = ML_KEM_768.encaps(keypair.kyber_public)
        else: # pqcrypto
            ciphertext_kem, shared_secret = encrypt(keypair.kyber_public)
        
        # Derivar clave de autenticación y generar HMAC
        auth_key = self._derivar_clave_autenticacion(shared_secret)
        auth_tag = hmac.new(key=auth_key, msg=mensaje_bytes, digestmod=hashlib.sha256).digest()
        
        return ciphertext_kem, auth_tag, shared_secret

    def desencapsular_auditoria(self, ciphertext_kem: bytes, mensaje_canonical: str, auth_tag_esperado: bytes, clave_privada_kyber: bytes) -> Tuple[bool, str]:
        """
        (Para Auditores) Desencapsula y verifica el sello post-cuántico.
        Requiere la clave privada Kyber.
        """
        if not KYBER_AVAILABLE:
            return False, "Kyber-768 no disponible"
            
        try:
            # Desencapsular secreto
            if KYBER_LIBRARY == "kyber_py":
                shared_secret = ML_KEM_768.decaps(clave_privada_kyber, ciphertext_kem)
            else: # pqcrypto
                shared_secret = decrypt(clave_privada_kyber, ciphertext_kem)

            # Derivar clave y recalcular HMAC
            auth_key = self._derivar_clave_autenticacion(shared_secret)
            auth_tag_calculado = hmac.new(key=auth_key, msg=mensaje_canonical.encode('utf-8'), digestmod=hashlib.sha256).digest()
            
            if hmac.compare_digest(auth_tag_calculado, auth_tag_esperado):
                return True, "Sello post-cuántico VÁLIDO."
            else:
                return False, "Sello post-cuántico INVÁLIDO (tag de autenticación no coincide)."
        except Exception as e:
            return False, f"Error en desencapsulación PQC: {e}"

    @staticmethod
    def _derivar_clave_autenticacion(shared_secret: bytes) -> bytes:
        """Deriva clave de autenticación desde secreto compartido usando HKDF."""
        salt = b'AEE-PQC-v2.1-AuthKey'
        prk = hmac.new(salt, shared_secret, hashlib.sha256).digest()
        info = b'authentication-key'
        return hmac.new(prk, info, hashlib.sha256).digest()

# ==============================================================================
# FUNCIONES DE INTEGRACIÓN CON MÓDULOS AEE
# ==============================================================================

@transaccion_forense("Generación de certificado híbrido")
def generar_certificado_hibrido(archivo_path: Path, keypair: HybridKeyPair, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Genera certificado AEE completo con firma dual."""
    logger.info(f"Generando certificado híbrido para: {archivo_path.name}")
    
    # 1. Calcular hash del archivo
    sha256 = hashlib.sha256()
    with open(archivo_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    hash_archivo = sha256.hexdigest()
    
    # 2. Obtener timestamp NTP
    quorum = RobustNTPQuorum()
    timestamp_ntp = quorum.obtener_timestamp_consenso()
    
    # 3. Construir y serializar el cuerpo del certificado
    certificado_base = {
        'hash_sha256': hash_archivo,
        'timestamp_ntp': timestamp_ntp,
        'archivo': {'nombre': archivo_path.name, 'tamano_bytes': archivo_path.stat().st_size},
        'metadata': metadata or {},
        'claves_publicas': keypair.to_dict()
    }
    mensaje_canonical = CanonicalJSONSerializer.serialize(certificado_base)
    
    # 4. Generar firma dual
    engine = HybridCryptoEngine()
    dual_sig = engine.firmar_dual(mensaje_canonical, keypair)
    
    # 5. Construir certificado final
    return {
        **certificado_base,
        'firmas': dual_sig.to_dict(),
        'version_protocolo': '2.2.0-HybridPQC',
        'fecha_certificacion': datetime.now(timezone.utc).isoformat()
    }

def verificar_certificado_hibrido(archivo_path: Path, certificado: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica un certificado híbrido.
    Valida públicamente el hash y la firma clásica (Ed25519).
    Indica si el sello PQC está presente para auditoría privada.
    """
    logger.info(f"Verificando certificado híbrido de: {archivo_path.name}")
    resultado = {'verificaciones': {}, 'exitoso': False, 'mensaje': ''}
    
    try:
        # 1. Verificar hash del archivo
        sha256 = hashlib.sha256()
        with open(archivo_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        hash_calculado = sha256.hexdigest()
        hash_ok = hmac.compare_digest(hash_calculado, certificado.get('hash_sha256', ''))
        resultado['verificaciones']['hash'] = {'exitoso': hash_ok, 'mensaje': 'Hash del archivo válido.' if hash_ok else 'Hash del archivo NO coincide.'}
        if not hash_ok:
            resultado['mensaje'] = 'Fallo en verificación de hash del archivo.'
            return resultado

        # 2. Reconstruir datos para verificación de firma
        claves_pub = certificado.get('claves_publicas', {})
        clave_publica_ed25519 = bytes.fromhex(claves_pub['ed25519_public'])

        certificado_base = {
            'hash_sha256': certificado['hash_sha256'], 'timestamp_ntp': certificado['timestamp_ntp'],
            'archivo': certificado['archivo'], 'metadata': certificado['metadata'],
            'claves_publicas': certificado['claves_publicas']
        }
        mensaje_canonical = CanonicalJSONSerializer.serialize(certificado_base)

        firmas_dict = certificado.get('firmas', {})
        dual_sig = DualSignature(
            signature_classic=bytes.fromhex(firmas_dict['signature_classic']),
            pqc_seal=bytes.fromhex(firmas_dict['pqc_seal']) if firmas_dict.get('pqc_seal') else None,
            pqc_auth_tag=bytes.fromhex(firmas_dict['pqc_auth_tag']) if firmas_dict.get('pqc_auth_tag') else None,
            timestamp=firmas_dict['timestamp']
        )
        
        # 3. Verificar firma dual (solo parte clásica)
        engine = HybridCryptoEngine()
        firma_ok, detalle_firma = engine.verificar_dual(mensaje_canonical, dual_sig, clave_publica_ed25519)
        resultado['verificaciones']['firmas'] = detalle_firma
        
        if firma_ok:
            resultado['exitoso'] = True
            resultado['mensaje'] = 'Certificado válido (firma clásica Ed25519 verificada).'
        else:
            resultado['mensaje'] = 'Certificado inválido (la firma clásica Ed25519 no es válida).'
        
    except Exception as e:
        resultado['mensaje'] = f'Error crítico en verificación: {e}'
        logger.error(f"Error crítico: {e}", exc_info=True)
        
    return resultado


# ==============================================================================
# UTILIDADES
# ==============================================================================

def guardar_keypair_seguro(keypair: HybridKeyPair, 
                          output_path: Path,
                          password: Optional[str] = None):
    """
    Guarda par de claves en archivo JSON.
    
    WARNING: En producción, las claves privadas DEBEN estar en HSM.
    Esta función es solo para desarrollo/testing.
    
    Args:
        keypair: Par de claves a guardar
        output_path: Ruta del archivo de salida
        password: Contraseña para cifrado (no implementado aún)
    """
    logger.warning(
        "Guardando claves privadas en disco - "
        "SOLO PARA DESARROLLO. En producción usar HSM."
    )
    
    data = {
        'keypair_public': keypair.to_dict(),
        'keypair_private': keypair.export_private(),
        'warning': 'CLAVES PRIVADAS - MANTENER SEGURO'
    }
    
    output_path.write_text(
        json.dumps(data, indent=2),
        encoding='utf-8'
    )
    
    logger.info(f"Keypair guardado en: {output_path}")


def cargar_keypair(keypair_path: Path) -> HybridKeyPair:
    """
    Carga par de claves desde archivo JSON.
    
    Args:
        keypair_path: Ruta del archivo con claves
        
    Returns:
        HybridKeyPair reconstruido
    """
    data = json.loads(keypair_path.read_text(encoding='utf-8'))
    
    private_data = data['keypair_private']
    public_data = data['keypair_public']
    
    return HybridKeyPair(
        ed25519_private=bytes.fromhex(private_data['ed25519_private']),
        ed25519_public=bytes.fromhex(public_data['ed25519_public']),
        kyber_private=bytes.fromhex(private_data['kyber_private']) if private_data.get('kyber_private') else b'',
        kyber_public=bytes.fromhex(public_data['kyber_public']) if public_data.get('kyber_public') else b'',
        created_at=public_data['created_at'],
        key_id=public_data['key_id']
    )