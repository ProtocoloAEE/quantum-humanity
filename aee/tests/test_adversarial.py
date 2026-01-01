"""
Tests Adversariales - Protocolo AEE v2.1
Valida que el sistema rechaza correctamente intentos de manipulación.

Modelo de Seguridad v2.1:
- Verificación estricta sin degradación silenciosa
- Fallos criptográficos deben lanzar excepciones claras
- Contenido alterado debe ser detectado y rechazado
"""

import sys
import os
from pathlib import Path

# Ajustar sys.path para encontrar el módulo aee
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir.parent) not in sys.path:
    sys.path.insert(0, str(parent_dir.parent))

import pytest
import hashlib
import json
import tempfile
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from aee.pqc_hybrid import HybridCryptoEngine, DualSignature, generar_certificado_hibrido, verificar_certificado_hibrido
from aee.core import CanonicalJSONSerializer


class TestAdversarial:
    """Tests adversariales para validar resistencia del Protocolo AEE v2.1"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.engine = HybridCryptoEngine()
        self.keypair = self.engine.generar_par_claves_hibrido()
        
        # Crear archivo de prueba temporal
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        self.temp_file.write(b"Contenido original de prueba para AEE Protocol v2.1")
        self.temp_file.close()
        self.file_path = Path(self.temp_file.name)
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        if self.file_path.exists():
            self.file_path.unlink()
    
    def test_1_verificacion_contenido_alterado_debe_fallar(self):
        """
        Test 1: Intento de verificación con contenido alterado (debe fallar)
        
        Escenario: Atacante modifica el archivo después de la certificación.
        Resultado esperado: Verificación debe fallar con hash no coincidente.
        """
        # 1. Generar certificado válido
        certificado = generar_certificado_hibrido(self.file_path, self.keypair)
        
        # 2. Alterar el archivo (simular ataque)
        with open(self.file_path, 'wb') as f:
            f.write(b"CONTENIDO ALTERADO POR ATACANTE - AEE Protocol v2.1")
        
        # 3. Intentar verificar (debe fallar)
        resultado = verificar_certificado_hibrido(self.file_path, certificado)
        
        # 4. Validar que la verificación falló
        assert not resultado['exitoso'], "La verificación debe fallar con contenido alterado"
        assert 'hash' in resultado['verificaciones'], "Debe incluir verificación de hash"
        assert not resultado['verificaciones']['hash']['exitoso'], "Hash debe ser inválido"
        assert 'NO coincide' in resultado['verificaciones']['hash']['mensaje'] or \
               'Hash del archivo NO coincide' in resultado['verificaciones']['hash']['mensaje'], \
               "Mensaje debe indicar fallo de hash"
    
    def test_2_verificacion_clave_publica_incorrecta_debe_fallar(self):
        """
        Test 2: Intento de verificación con clave pública que no corresponde (debe fallar)
        
        Escenario: Atacante intenta verificar con una clave pública diferente.
        Resultado esperado: Verificación de firma debe fallar.
        """
        # 1. Generar certificado válido
        certificado = generar_certificado_hibrido(self.file_path, self.keypair)
        
        # 2. Generar un par de claves diferente (simular atacante)
        keypair_atacante = self.engine.generar_par_claves_hibrido()
        
        # 3. Reemplazar la clave pública en el certificado con la del atacante
        certificado['claves_publicas']['ed25519_public'] = keypair_atacante.ed25519_public.hex()
        
        # 4. Reconstruir mensaje canónico con clave pública incorrecta
        cert_base = {
            'hash_sha256': certificado['hash_sha256'],
            'timestamp_ntp': certificado['timestamp_ntp'],
            'archivo': certificado['archivo'],
            'metadata': certificado.get('metadata', {}),
            'claves_publicas': certificado['claves_publicas']
        }
        mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)
        
        # 5. Intentar verificar con clave pública incorrecta
        firmas_dict = certificado.get('firmas', {})
        dual_sig = DualSignature(
            signature_classic=bytes.fromhex(firmas_dict['signature_classic']),
            pqc_seal=bytes.fromhex(firmas_dict['pqc_seal']) if firmas_dict.get('pqc_seal') else None,
            pqc_auth_tag=bytes.fromhex(firmas_dict['pqc_auth_tag']) if firmas_dict.get('pqc_auth_tag') else None,
            timestamp=firmas_dict['timestamp']
        )
        
        # 6. Verificar (debe fallar porque la firma no corresponde a esta clave pública)
        firma_ok, detalle = self.engine.verificar_dual(
            mensaje_canonical,
            dual_sig,
            keypair_atacante.ed25519_public  # Clave pública incorrecta
        )
        
        # 7. Validar que la verificación falló
        assert not firma_ok, "La verificación debe fallar con clave pública incorrecta"
        assert not detalle['ed25519_valido'], "Ed25519 debe ser inválido"
        assert 'inválida' in detalle['mensaje_ed25519'].lower() or \
               'invalid' in detalle['mensaje_ed25519'].lower(), \
               "Mensaje debe indicar firma inválida"
    
    def test_3_verificacion_flujo_normal_debe_exitoso(self):
        """
        Test 3: Verificación exitosa de un flujo normal
        
        Escenario: Certificación y verificación con parámetros correctos.
        Resultado esperado: Verificación debe ser exitosa.
        """
        # 1. Generar certificado válido
        certificado = generar_certificado_hibrido(self.file_path, self.keypair)
        
        # 2. Verificar sin alteraciones
        resultado = verificar_certificado_hibrido(self.file_path, certificado)
        
        # 3. Validar que la verificación fue exitosa
        assert resultado['exitoso'], "La verificación debe ser exitosa en flujo normal"
        assert 'hash' in resultado['verificaciones'], "Debe incluir verificación de hash"
        assert resultado['verificaciones']['hash']['exitoso'], "Hash debe ser válido"
        assert 'firmas' in resultado['verificaciones'], "Debe incluir verificación de firmas"
        assert resultado['verificaciones']['firmas']['ed25519_valido'], "Firma Ed25519 debe ser válida"
        assert 'válida' in resultado['verificaciones']['firmas']['mensaje_ed25519'].lower() or \
               'valid' in resultado['verificaciones']['firmas']['mensaje_ed25519'].lower(), \
               "Mensaje debe indicar firma válida"
        
        # 4. Validar estructura del resultado
        assert 'mensaje' in resultado, "Debe incluir mensaje descriptivo"
        assert 'verificaciones' in resultado, "Debe incluir detalles de verificaciones"


if __name__ == "__main__":
    """
    Ejecución directa de tests (para desarrollo)
    """
    import sys
    
    print("=" * 70)
    print("TESTS ADVERSARIALES - PROTOCOLO AEE v2.1")
    print("=" * 70)
    print()
    
    test_suite = TestAdversarial()
    
    try:
        test_suite.setup_method()
        
        print("Test 1: Verificacion con contenido alterado...")
        try:
            test_suite.test_1_verificacion_contenido_alterado_debe_fallar()
            print("  [PASSED]")
        except AssertionError as e:
            print(f"  [FAILED]: {e}")
            sys.exit(1)
        
        print("Test 2: Verificacion con clave publica incorrecta...")
        try:
            test_suite.test_2_verificacion_clave_publica_incorrecta_debe_fallar()
            print("  [PASSED]")
        except AssertionError as e:
            print(f"  [FAILED]: {e}")
            sys.exit(1)
        
        print("Test 3: Verificacion exitosa de flujo normal...")
        try:
            test_suite.test_3_verificacion_flujo_normal_debe_exitoso()
            print("  [PASSED]")
        except AssertionError as e:
            print(f"  [FAILED]: {e}")
            sys.exit(1)
        
        print()
        print("=" * 70)
        print("[SUCCESS] TODOS LOS TESTS ADVERSARIALES PASARON")
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] ERROR CRITICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        test_suite.teardown_method()

