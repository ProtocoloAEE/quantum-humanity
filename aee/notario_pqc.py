"""
Módulo Notario AEE
Orquesta la creación de certificados de evidencia digital.
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from aee.core import RobustNTPQuorum, CanonicalJSONSerializer, ForensicErrorHandler, transaccion_forense, logger

class NotarioAEE:
    """
    Orquesta el proceso de certificación de evidencia digital (AEE).
    Utiliza los módulos robustos de aee.core para garantizar
    integridad, temporalidad y autenticidad.
    """
    
    def __init__(self, auditor_id: str):
        """
        Inicializa el Notario con la identidad del auditor. 
        
        Args:
            auditor_id: Identificador único del auditor (e.g., email, DNI).
        """
        self.auditor_id = auditor_id
        self.version = "2.2.0-Refactored"
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self.public_key_hex = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        logger.info(f"Notario AEE inicializado para '{auditor_id}'.")
        logger.info(f"Clave pública Ed25519: {self.public_key_hex[:16]}...")

    @staticmethod
    def _calcular_hash_archivo(file_path: Path) -> str:
        """Calcula el hash SHA-256 de un archivo de forma eficiente."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _obtener_metadatos_forenses(file_path: Path) -> dict:
        """Recopila metadatos de bajo nivel del sistema de archivos."""
        stats = file_path.stat()
        return {
            "inode": stats.st_ino,
            "device": stats.st_dev,
            "size_bytes": stats.st_size,
            "os_mtime_iso": datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc).isoformat(),
            "os_ctime_iso": datetime.fromtimestamp(stats.st_ctime, tz=timezone.utc).isoformat(),
        }

    @transaccion_forense("Certificación de Archivo AEE")
    def certificar_archivo(self, file_path_str: str, certificado_output_path_str: str):
        """
        Crea un certificado de evidencia digital para un archivo.
        
        Modelo de Seguridad v2.1:
        - Transacción forense con rollback automático en caso de error
        - Verificación de existencia de archivo antes de procesar
        - Quórum NTP obligatorio (no se permite timestamp local como fallback)
        - Firma Ed25519 obligatoria (no se permite degradación silenciosa)
        
        Args:
            file_path_str: Ruta al archivo que se va a certificar.
            certificado_output_path_str: Ruta donde se guardará el certificado JSON.
        
        Returns:
            Ruta al certificado generado.
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            RuntimeError: Si falla la generación de firma o timestamp NTP
        """
        file_path = Path(file_path_str)
        certificado_output_path = Path(certificado_output_path_str)
        
        if not file_path.exists():
            raise FileNotFoundError(f"El archivo a certificar no existe: {file_path}")

        # 1. Obtener timestamp de consenso (OBLIGATORIO - no se permite fallback local)
        try:
            ntp_quorum = RobustNTPQuorum()
            timestamp_data = ntp_quorum.obtener_timestamp_consenso()
        except Exception as e:
            logger.error(f"Fallo crítico en obtención de timestamp NTP: {e}")
            raise RuntimeError(
                f"Error en quórum NTP (no se permite degradación silenciosa): {str(e)}"
            ) from e

        # 2. Calcular hash del archivo
        file_hash = self._calcular_hash_archivo(file_path)

        # 3. Recopilar metadatos forenses
        forensic_metadata = self._obtener_metadatos_forenses(file_path)

        # 4. Construir el payload para la firma
        # Este payload contiene los elementos críticos que la firma protege.
        payload_firmado = {
            "hash_sha256": file_hash,
            "timestamp_iso": timestamp_data['timestamp_iso'],
            "auditor_id": self.auditor_id,
            "protocolo_version": self.version
        }

        # 5. Serializar el payload de forma canónica
        payload_canonico_str = CanonicalJSONSerializer.serialize(payload_firmado)
        payload_canonico_bytes = payload_canonico_str.encode('utf-8')

        # 6. Firmar el payload canónico
        # Modelo de Seguridad v2.1: No se permite degradación silenciosa
        try:
            signature = self._private_key.sign(payload_canonico_bytes).hex()
        except Exception as e:
            logger.error(f"Fallo crítico en firma Ed25519: {e}")
            raise RuntimeError(
                f"Error en firma digital (no se permite degradación silenciosa): {str(e)}"
            ) from e

        # 7. Construir el certificado final completo
        certificado = {
            "encabezado": {
                "titulo": "Certificado de Evidencia Digital AEE",
                "version_protocolo": self.version,
                "id_certificado": f"AEE-{int(timestamp_data['timestamp_unix'])}-{file_hash[:8]}",
            },
            "auditor": {
                "id": self.auditor_id,
                "algoritmo_clave": "Ed25519",
                "clave_publica_hex": self.public_key_hex,
            },
            "evidencia": {
                "nombre_archivo": file_path.name,
                "hash_sha256": file_hash,
                "metadatos_forenses": forensic_metadata,
            },
            "sello_temporal": timestamp_data,
            "firma_digital": {
                "algoritmo": "Ed25519",
                "valor_hex": signature,
                "payload_firmado": payload_firmado  # Incluir el payload claro para facilitar la verificación
            }
        }
        
        # 8. Guardar el certificado en un archivo JSON
        with open(certificado_output_path, 'w', encoding='utf-8') as f:
            json.dump(certificado, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Certificado AEE generado exitosamente en: {certificado_output_path}")
        return str(certificado_output_path)

if __name__ == '__main__':
    # Ejemplo de uso directo del Notario
    print("--- Ejecutando demostración del Notario AEE ---")
    
    # Crear un archivo de prueba
    Path("prueba_notario.txt").write_text("Esta es una prueba para el Notario AEE.", encoding='utf-8')
    
    try:
        # 1. Inicializar el Notario
        notario = NotarioAEE(auditor_id="notario.demo@aee-protocol.org")
        
        # 2. Certificar el archivo
        certificado_path = notario.certificar_archivo(
            "prueba_notario.txt",
            "certificado_demo.json"
        )
        
        print(f"\n✅ Proceso de certificación completado.")
        print(f"   Archivo de prueba: prueba_notario.txt")
        print(f"   Certificado: {certificado_path}")
        
        # 3. (Opcional) Mostrar contenido del certificado
        with open(certificado_path, 'r', encoding='utf-8') as f:
            print("\n--- Contenido del Certificado ---")
            print(f.read())
            print("---------------------------------\n")

    except Exception as e:
        logger.error(f"Falló la demostración del Notario AEE: {e}", exc_info=True)
    
    finally:
        # Limpiar archivos de prueba
        Path("prueba_notario.txt").unlink(missing_ok=True)
        Path("certificado_demo.json").unlink(missing_ok=True)
        print("--- Fin de la demostración ---")
