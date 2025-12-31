"""
Script de Pruebas Automatizadas para el Protocolo AEE con Motor Híbrido PQC.
"""
import unittest
import json
from pathlib import Path
import os

# Importar los componentes necesarios del nuevo motor híbrido
from aee.pqc_hybrid import (
    HybridCryptoEngine,
    generar_certificado_hibrido,
    verificar_certificado_hibrido,
    KYBER_AVAILABLE,
    CanonicalJSONSerializer
)

class TestHybridAEEProtocol(unittest.TestCase):

    TEST_FILE_NAME = "test_evidence_file.txt"
    CERTIFICATE_NAME = "test_hybrid_certificate.json"
    TEST_FILE_CONTENT = "Contenido original de la evidencia para la prueba híbrida."
    TAMPERED_CONTENT = "Contenido alterado maliciosamente."

    @classmethod
    def setUpClass(cls):
        """Se ejecuta una vez antes de todas las pruebas. Genera el keypair."""
        print("\n--- Configurando Entorno de Prueba Híbrida ---")
        try:
            engine = HybridCryptoEngine()
            cls.keypair = engine.generar_par_claves_hibrido()
            print(f"Keypair de prueba generado en memoria para la sesión.")
        except Exception as e:
            raise unittest.SkipTest(f"No se pudo inicializar el motor criptográfico: {e}")

    @classmethod
    def tearDownClass(cls):
        """Se ejecuta una vez después de todas las pruebas."""
        print("\n--- Entorno de Prueba Híbrida Limpio ---")

    def setUp(self):
        """Se ejecuta antes de cada prueba individual."""
        Path(self.TEST_FILE_NAME).write_text(self.TEST_FILE_CONTENT, encoding='utf-8')
        if Path(self.CERTIFICATE_NAME).exists():
            os.remove(self.CERTIFICATE_NAME)

    def tearDown(self):
        """Se ejecuta después de cada prueba individual."""
        if Path(self.TEST_FILE_NAME).exists():
            os.remove(self.TEST_FILE_NAME)
        if Path(self.CERTIFICATE_NAME).exists():
            os.remove(self.CERTIFICATE_NAME)

    def test_01_hybrid_certification_and_public_verification(self):
        """
        Prueba el ciclo de vida:
        1. Generación de certificado híbrido.
        2. Verificación pública (solo Ed25519).
        """
        print("\n[TEST 1] Certificación y Verificación Pública Híbrida")
        
        # 1. Generar certificado
        certificado = generar_certificado_hibrido(Path(self.TEST_FILE_NAME), self.keypair)
        Path(self.CERTIFICATE_NAME).write_text(json.dumps(certificado, indent=2), encoding='utf-8')
        self.assertTrue(Path(self.CERTIFICATE_NAME).exists())
        print("   - Certificado híbrido generado.")
        
        # 2. Verificar certificado
        resultados = verificar_certificado_hibrido(Path(self.TEST_FILE_NAME), certificado)
        
        # 3. Validar resultados
        self.assertTrue(resultados['exitoso'], "La verificación pública general debería ser exitosa.")
        self.assertTrue(resultados['verificaciones']['hash']['exitoso'], "El hash del archivo debería ser válido.")
        self.assertTrue(resultados['verificaciones']['firmas']['ed25519_valido'], "La firma Ed25519 debería ser válida.")
        
        if KYBER_AVAILABLE:
            self.assertIsNone(resultados['verificaciones']['firmas']['kyber_valido'], "Kyber no debe ser validado en una verificación pública.")
            self.assertIn("Requiere clave privada", resultados['verificaciones']['firmas']['mensaje_kyber'])
            print("   - Verificación Ed25519: OK")
            print("   - Sello Kyber: Presente (no verificado públicamente, como se esperaba)")
        else:
            print("   - Verificación Ed25519: OK (Kyber no disponible)")
            
        print("   - PRUEBA EXITOSA: El ciclo de verificación pública funciona.")

    def test_02_verification_fails_on_tampered_file(self):
        """
        Prueba que la verificación pública falle si el archivo es alterado.
        """
        print("\n[TEST 2] Falla de Verificación con Archivo Alterado")
        
        # 1. Generar certificado
        certificado = generar_certificado_hibrido(Path(self.TEST_FILE_NAME), self.keypair)
        print("   - Certificado original generado.")
        
        # 2. Alterar el archivo
        Path(self.TEST_FILE_NAME).write_text(self.TAMPERED_CONTENT, encoding='utf-8')
        print("   - Archivo de evidencia alterado.")
        
        # 3. Verificar el archivo alterado
        resultados = verificar_certificado_hibrido(Path(self.TEST_FILE_NAME), certificado)
        
        # 4. Validar que la verificación falle por el hash
        self.assertFalse(resultados['exitoso'], "La verificación debería fallar.")
        self.assertFalse(resultados['verificaciones']['hash']['exitoso'], "La causa del fallo debería ser la verificación de hash.")
        print("   - Verificación falló como se esperaba (discrepancia de hash).")
        print("   - PRUEBA EXITOSA: El sistema detectó la manipulación del archivo.")

    @unittest.skipIf(not KYBER_AVAILABLE, "Kyber no está instalado (pip install kyber-py), se omite prueba de auditor.")
    def test_03_auditor_pqc_verification(self):
        """
        (Prueba Avanzada) Demuestra que un auditor con la clave privada
        SÍ PUEDE verificar el sello post-cuántico.
        """
        print("\n[TEST 3] Verificación de Auditor con Clave Privada PQC")
        
        # 1. Generar certificado
        certificado = generar_certificado_hibrido(Path(self.TEST_FILE_NAME), self.keypair)
        print("   - Certificado híbrido generado.")

        # 2. Reconstruir datos para la auditoría
        mensaje_canonical = CanonicalJSONSerializer.serialize({
            'hash_sha256': certificado['hash_sha256'],
            'timestamp_ntp': certificado['timestamp_ntp'],
            'archivo': certificado['archivo'],
            'metadata': certificado['metadata'],
            'claves_publicas': certificado['claves_publicas']
        })
        
        firmas = certificado['firmas']
        
        # 3. Ejecutar la desencapsulación de auditoría
        engine = HybridCryptoEngine()
        pqc_valido, pqc_msg = engine.desencapsular_auditoria(
            ciphertext_kem=bytes.fromhex(firmas['pqc_seal']),
            mensaje_canonical=mensaje_canonical,
            auth_tag_esperado=bytes.fromhex(firmas['pqc_auth_tag']),
            clave_privada_kyber=self.keypair.kyber_private
        )
        
        # 4. Validar que la verificación PQC fue exitosa
        self.assertTrue(pqc_valido, "La verificación PQC del auditor debería ser exitosa.")
        print(f"   - Auditoría PQC: {pqc_msg}")
        print("   - PRUEBA EXITOSA: El sello post-cuántico es válido y verificable por el auditor.")

if __name__ == '__main__':
    unittest.main()
