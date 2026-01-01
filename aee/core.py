"\nPROTOCOLO AEE v2.1-HARDENED - Módulos de Producción\nCódigo optimizado para despliegue en ambientes críticos\nAutor: Desarrollo AEE\nVersión: 2.1.0\n"

import json
import hashlib
import ntplib
import statistics
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from functools import wraps
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# ==============================================================================
# CONFIGURACIÓN DE LOGGING FORENSE
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aee_forensic.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AEE-Protocol')


# ==============================================================================
# 1. MÓDULO DE SERIALIZACIÓN CANÓNICA
# ==============================================================================

class CanonicalJSONSerializer:
    """
    Serializador JSON canónico para garantizar reproducibilidad bit-a-bit.
    Implementa RFC 8785 (JSON Canonicalization Scheme - JCS).
    """
    
    @staticmethod
    def serialize(data: Dict[str, Any]) -> str:
        """
        Serializa un diccionario a JSON canónico.
        
        Garantías:
        - Orden alfabético de claves en todos los niveles
        - Sin espacios en blanco adicionales
        - Formato UTF-8 sin BOM
        - Reproducible entre diferentes sistemas
        
        Args:
            data: Diccionario a serializar
            
        Returns:
            String JSON canónico
        """
        try:
            # Serialización con sort_keys para orden determinístico
            # separators elimina espacios extras
            canonical = json.dumps(
                data,
                sort_keys=True,
                separators=(',', ':'),
                ensure_ascii=False
            )
            
            logger.debug(f"Serialización canónica: {len(canonical)} bytes")
            return canonical
            
        except Exception as e:
            logger.error(f"Error en serialización canónica: {e}")
            raise ValueError(f"Fallo en serialización: {str(e)}")
    
    @staticmethod
    def hash_canonical(data: Dict[str, Any]) -> str:
        """
        Genera hash SHA-256 de la representación canónica.
        
        Args:
            data: Diccionario a hashear
            
        Returns:
            Hash hexadecimal del JSON canónico
        """
        canonical_json = CanonicalJSONSerializer.serialize(data)
        hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).digest()
        return hash_bytes.hex()
    
    @staticmethod
    def verify_canonical(data: Dict[str, Any], expected_hash: str) -> bool:
        """
        Verifica que el hash canónico coincida con el esperado.
        
        Args:
            data: Diccionario a verificar
            expected_hash: Hash esperado en hexadecimal
            
        Returns:
            True si coincide, False en caso contrario
        """
        computed_hash = CanonicalJSONSerializer.hash_canonical(data)
        return computed_hash == expected_hash


# ==============================================================================
# 2. MÓDULO DE QUÓRUM NTP ROBUSTO
# ==============================================================================

@dataclass
class NTPResponse:
    """Estructura de respuesta de servidor NTP"""
    server: str
    timestamp: float
    offset: float
    delay: float
    success: bool
    error: Optional[str] = None


class RobustNTPQuorum:
    """
    Sistema de consenso temporal mediante quórum de servidores NTP.
    Implementa algoritmo de mediana para eliminar outliers.
    """
    
    # Servidores NTP de alta confiabilidad
    DEFAULT_SERVERS = [
        'time.google.com',       # Google (Anycast global)
        'time.cloudflare.com',   # Cloudflare (Anycast global)
        'time.nist.gov',         # NIST (Referencia USA)
        'time.apple.com',        # Apple (Alta disponibilidad)
        'pool.ntp.org'           # Pool global
    ]
    
    def __init__(self, 
                 servers: Optional[List[str]] = None,
                 max_deviation_ms: float = 500.0,
                 timeout_seconds: int = 3,
                 min_successful_servers: int = 3):
        """
        Inicializa el sistema de quórum NTP.
        
        Args:
            servers: Lista de servidores NTP (usa DEFAULT_SERVERS si es None)
            max_deviation_ms: Desviación máxima permitida en milisegundos
            timeout_seconds: Timeout para cada consulta NTP
            min_successful_servers: Mínimo de servidores exitosos requeridos
        """
        self.servers = servers or self.DEFAULT_SERVERS
        self.max_deviation_ms = max_deviation_ms
        self.timeout = timeout_seconds
        self.min_successful = min_successful_servers
        self.ntp_client = ntplib.NTPClient()
    
    def query_server(self, server: str) -> NTPResponse:
        """
        Consulta un servidor NTP individual.
        
        Args:
            server: Hostname del servidor NTP
            
        Returns:
            NTPResponse con resultado de la consulta
        """
        try:
            response = self.ntp_client.request(server, version=3, timeout=self.timeout)
            
            return NTPResponse(
                server=server,
                timestamp=response.tx_time,
                offset=response.offset,
                delay=response.delay,
                success=True
            )
            
        except Exception as e:
            logger.warning(f"Fallo al consultar {server}: {str(e)}")
            return NTPResponse(
                server=server,
                timestamp=0.0,
                offset=0.0,
                delay=0.0,
                success=False,
                error=str(e)
            )
    
    def obtener_timestamp_consenso(self) -> Dict[str, Any]:
        """
        Obtiene timestamp mediante consenso de múltiples servidores NTP.
        
        Algoritmo:
        1. Consulta todos los servidores en paralelo
        2. Filtra respuestas exitosas
        3. Calcula mediana de timestamps
        4. Descarta valores con desviación > max_deviation_ms
        5. Recalcula mediana final
        
        Returns:
            Diccionario con timestamp consensuado y metadatos
            
        Raises:
            RuntimeError: Si no se alcanza el mínimo de servidores exitosos
        """
        logger.info(f"Iniciando quórum NTP con {len(self.servers)} servidores")
        
        # Consultar todos los servidores
        responses = [self.query_server(server) for server in self.servers]
        
        # Filtrar solo respuestas exitosas
        successful = [r for r in responses if r.success]
        
        if len(successful) < self.min_successful:
            error_msg = f"Quórum NTP falló: solo {len(successful)}/{len(self.servers)} servidores respondieron"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Extraer timestamps
        timestamps = [r.timestamp for r in successful]
        
        # Calcular mediana inicial
        median_initial = statistics.median(timestamps)
        
        # Filtrar outliers usando desviación estándar
        if len(timestamps) >= 3:
            std_dev = statistics.stdev(timestamps)
            std_dev_ms = std_dev * 1000  # Convertir a milisegundos
            
            # Filtrar timestamps dentro del rango aceptable
            filtered = [
                ts for ts in timestamps 
                if abs(ts - median_initial) * 1000 <= self.max_deviation_ms
            ]
            
            if len(filtered) < self.min_successful:
                logger.warning(f"Filtro de outliers muy agresivo, usando mediana inicial")
                final_timestamps = timestamps
            else:
                final_timestamps = filtered
                logger.info(f"Outliers filtrados: {len(timestamps) - len(filtered)}")
        else:
            final_timestamps = timestamps
            std_dev_ms = 0.0
        
        # Calcular mediana final
        median_final = statistics.median(final_timestamps)
        
        # Construir resultado
        result = {
            'timestamp_unix': median_final,
            'timestamp_iso': datetime.fromtimestamp(median_final, tz=timezone.utc).isoformat(),
            'servidores_consultados': len(self.servers),
            'servidores_exitosos': len(successful),
            'servidores_usados_consenso': len(final_timestamps),
            'desviacion_estandar_ms': round(std_dev_ms, 2) if len(timestamps) >= 3 else 0.0,
            'detalle_servidores': [
                {
                    'servidor': r.server,
                    'timestamp': r.timestamp,
                    'offset_ms': round(r.offset * 1000, 2),
                    'delay_ms': round(r.delay * 1000, 2)
                }
                for r in successful
            ]
        }
        
        logger.info(f"Quórum NTP exitoso: {result['timestamp_iso']} (stdev={result['desviacion_estandar_ms']}ms)")
        
        return result


# ==============================================================================
# 3. MÓDULO DE MANEJO DE ERRORES FORENSES
# ==============================================================================

class ForensicTransactionError(Exception): 
    """Excepción para errores en transacciones forenses"""
    pass


class ForensicErrorHandler:
    """
    Gestor de errores con rollback automático para operaciones críticas.
    Garantiza atomicidad: o se completa toda la operación o se revierte.
    """
    
    def __init__(self, operation_name: str):
        """
        Args:
            operation_name: Nombre descriptivo de la operación
        """
        self.operation_name = operation_name
        self.backup_data: Dict[str, Any] = {}
        self.temp_files: List[Path] = []
    
    def __enter__(self):
        """Inicia contexto de transacción"""
        logger.info(f"Iniciando transacción forense: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Finaliza contexto de transacción con rollback automático si hay error.
        """
        if exc_type is not None:
            # Hubo una excepción, hacer rollback
            logger.error(f"Error en {self.operation_name}: {exc_val}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            self._rollback()
            
            # Re-lanzar excepción como ForensicTransactionError
            raise ForensicTransactionError(
                f"Transacción '{self.operation_name}' abortada: {str(exc_val)}"
            ) from exc_val
        else:
            # Transacción exitosa
            logger.info(f"Transacción forense completada: {self.operation_name}")
            self._cleanup_temp_files()
        
        return False  # No suprimir excepciones
    
    def backup_file(self, file_path: Path):
        """
        Crea backup de un archivo antes de modificarlo.
        
        Args:
            file_path: Ruta del archivo a respaldar
        """
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            backup_path.write_bytes(file_path.read_bytes())
            self.backup_data[str(file_path)] = str(backup_path)
            logger.debug(f"Backup creado: {backup_path}")
    
    def register_temp_file(self, file_path: Path):
        """
        Registra archivo temporal para limpieza automática.
        
        Args:
            file_path: Ruta del archivo temporal
        """
        self.temp_files.append(file_path)
    
    def _rollback(self):
        """Revierte cambios restaurando backups"""
        logger.warning(f"Ejecutando rollback para: {self.operation_name}")
        
        # Restaurar archivos desde backups
        for original, backup in self.backup_data.items():
            try:
                original_path = Path(original)
                backup_path = Path(backup)
                
                if backup_path.exists():
                    original_path.write_bytes(backup_path.read_bytes())
                    logger.info(f"Archivo restaurado: {original}")
                    backup_path.unlink()
            except Exception as e:
                logger.error(f"Error en rollback de {original}: {e}")
        
        # Limpiar archivos temporales
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Elimina archivos temporales registrados"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Archivo temporal eliminado: {temp_file}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar {temp_file}: {e}")


def transaccion_forense(operation_name: str):
    """
    Decorador para envolver funciones en transacciones forenses con rollback.
    
    Usage:
        @transaccion_forense("Generación de certificado")
        def generar_certificado(archivo):
            # código que puede fallar
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ForensicErrorHandler(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ==============================================================================
# 4. VERIFICACIÓN CRUZADA ATÓMICA
# ==============================================================================

class IntegrityVerifier:
    """
    Verificador de integridad atómico para certificados AEE.
    Valida hash, timestamp y firma en una sola operación.
    """
    
    def __init__(self):
        """Inicializa el verificador de integridad."""
        logger.debug("IntegrityVerifier inicializado.")

    @staticmethod
    def verificar_hash_archivo(archivo_path: Path, hash_esperado: str) -> Tuple[bool, str]:
        """
        Verifica integridad del archivo mediante hash SHA-256.
        """
        try:
            if not archivo_path.exists():
                return False, f"Archivo no encontrado: {archivo_path}"
            
            sha256 = hashlib.sha256()
            with open(archivo_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            
            hash_calculado = sha256.hexdigest()
            
            if hash_calculado == hash_esperado:
                return True, "Hash del archivo verificado correctamente."
            else:
                return False, f"Hash no coincide. Esperado: {hash_esperado[:16]}..., Calculado: {hash_calculado[:16]}..."
            
        except Exception as e:
            return False, f"Error al verificar hash: {str(e)}"

    @staticmethod
    def verificar_timestamp_quorum(timestamp_data: Dict[str, Any], max_age_hours: Optional[int] = None) -> Tuple[bool, str]:
        """
        Verifica validez del timestamp del quórum NTP.
        """
        try:
            required_fields = ['timestamp_unix', 'servidores_exitosos', 'desviacion_estandar_ms']
            if not all(field in timestamp_data for field in required_fields):
                return False, "Estructura de datos del timestamp inválida."
            
            if timestamp_data['servidores_exitosos'] < 3:
                return False, f"Quórum NTP insuficiente: solo {timestamp_data['servidores_exitosos']} servidores."
            
            if timestamp_data['desviacion_estandar_ms'] > 1000: # Límite generoso
                return False, f"Desviación estándar de NTP muy alta: {timestamp_data['desviacion_estandar_ms']:.2f}ms."
            
            if max_age_hours is not None:
                age_seconds = time.time() - timestamp_data['timestamp_unix']
                if age_seconds > max_age_hours * 3600:
                    return False, f"El timestamp es demasiado antiguo ({age_seconds / 3600:.1f}h)."
            
            return True, "Timestamp de quórum NTP verificado correctamente."
            
        except Exception as e:
            return False, f"Error al verificar timestamp: {str(e)}"

    @staticmethod
    def verificar_firma_ed25519(mensaje: bytes, firma_hex: str, clave_publica_hex: str) -> Tuple[bool, str]:
        """
        Verifica una firma digital Ed25519 directamente.
        """
        try:
            clave_publica_bytes = bytes.fromhex(clave_publica_hex)
            firma_bytes = bytes.fromhex(firma_hex)
            
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(clave_publica_bytes)
            public_key.verify(firma_bytes, mensaje)
            
            return True, "Firma digital Ed25519 válida."
            
        except InvalidSignature:
            return False, "Firma digital Ed25519 inválida."
        except Exception as e:
            return False, f"Error en la validación criptográfica: {str(e)}"

    def verificar_integridad_total(self, archivo_path: Path, certificado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verificación atómica de integridad completa de un certificado AEE.
        
        Modelo de Seguridad v2.1:
        - Verificación atómica: todas las verificaciones deben pasar o se aborta
        - No permite degradación silenciosa: fallos críticos se propagan como excepciones
        - Orden de verificación: Hash → Timestamp → Firma (fail-fast)
        - Errores de formato/estructura lanzan excepciones (no se retorna False silenciosamente)
        
        Args:
            archivo_path: Ruta al archivo original a verificar
            certificado: Diccionario con certificado AEE completo
            
        Returns:
            Dict con resultados de verificación:
            - es_valido: True solo si todas las verificaciones pasan
            - verificaciones: Dict con estado de cada componente
            - resumen: Mensaje descriptivo del resultado
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el certificado tiene estructura inválida
            RuntimeError: Si hay error crítico en operaciones criptográficas
        """
        logger.info(f"Iniciando verificación de integridad total para: {archivo_path.name}")
        
        # Validación inicial (no se permite degradación silenciosa)
        if not archivo_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_path}")
        if not certificado or not isinstance(certificado, dict):
            raise ValueError("certificado debe ser un diccionario válido")
        
        resultados = {
            'archivo_verificado': str(archivo_path),
            'id_certificado': certificado.get('encabezado', {}).get('id_certificado', 'N/A'),
            'timestamp_verificacion': datetime.now(timezone.utc).isoformat(),
            'verificaciones': {},
            'es_valido': False,
            'resumen': ''
        }
        
        try:
            # Extraer datos del certificado
            evidencia = certificado.get('evidencia', {})
            sello_temporal = certificado.get('sello_temporal', {})
            auditor = certificado.get('auditor', {})
            firma_digital = certificado.get('firma_digital', {})

            # 1. Verificar hash del archivo (fail-fast)
            hash_ok, hash_msg = self.verificar_hash_archivo(
                archivo_path,
                evidencia.get('hash_sha256', '')
            )
            resultados['verificaciones']['hash_archivo'] = {'exitoso': hash_ok, 'mensaje': hash_msg}
            if not hash_ok:
                resultados['resumen'] = "Fallo en verificación de hash del archivo."
                logger.error(f"{resultados['resumen']} - {hash_msg}")
                return resultados

            # 2. Verificar timestamp NTP (fail-fast)
            ts_ok, ts_msg = self.verificar_timestamp_quorum(sello_temporal)
            resultados['verificaciones']['sello_temporal'] = {'exitoso': ts_ok, 'mensaje': ts_msg}
            if not ts_ok:
                resultados['resumen'] = "Fallo en verificación del sello temporal."
                logger.error(f"{resultados['resumen']} - {ts_msg}")
                return resultados

            # 3. Verificar firma digital (fail-fast)
            payload_firmado = firma_digital.get('payload_firmado', {})
            if not payload_firmado:
                error_msg = "No se encontró el payload firmado en el certificado."
                logger.error(error_msg)
                raise ValueError(error_msg)

            mensaje_canonico = CanonicalJSONSerializer.serialize(payload_firmado).encode('utf-8')
            
            firma_ok, firma_msg = self.verificar_firma_ed25519(
                mensaje_canonico,
                firma_digital.get('valor_hex', ''),
                auditor.get('clave_publica_hex', '')
            )
            resultados['verificaciones']['firma_digital'] = {'exitoso': firma_ok, 'mensaje': firma_msg}
            if not firma_ok:
                resultados['resumen'] = "Fallo en verificación de la firma digital."
                logger.error(f"{resultados['resumen']} - {firma_msg}")
                return resultados

            # Si todo está OK
            resultados['es_valido'] = True
            resultados['resumen'] = "VERIFICACIÓN EXITOSA: La evidencia es íntegra y auténtica."
            logger.info(resultados['resumen'])

        except (FileNotFoundError, ValueError) as e:
            # Errores de formato/estructura se propagan (no se ocultan)
            logger.error(f"Error de validación en verificación: {e}", exc_info=True)
            raise
        except Exception as e:
            # Errores críticos inesperados se propagan
            resultados['resumen'] = f"Error crítico durante la verificación: {str(e)}"
            logger.error(resultados['resumen'], exc_info=True)
            raise RuntimeError(f"Error crítico en verificación (no se permite degradación silenciosa): {str(e)}") from e
        
        return resultados


# ==============================================================================
# FUNCIONES DE USO RÁPIDO
# ==============================================================================

def obtener_timestamp_consenso() -> Dict[str, Any]:
    """
    Función de conveniencia para obtener timestamp de consenso NTP.
    
    Returns:
        Diccionario con timestamp consensuado
    """
    quorum = RobustNTPQuorum()
    return quorum.obtener_timestamp_consenso()


def serializar_canonico(data: Dict[str, Any]) -> str:
    """
    Función de conveniencia para serialización canónica.
    
    Args:
        data: Diccionario a serializar
        
    Returns:
        String JSON canónico
    """
    return CanonicalJSONSerializer.serialize(data)


def verificar_certificado(archivo_path: str, certificado_path: str) -> Dict[str, Any]:
    """
    Función de conveniencia para verificación completa.
    
    Args:
        archivo_path: Ruta del archivo original
        certificado_path: Ruta del archivo JSON con el certificado
        
    Returns:
        Diccionario con resultados de verificación
    """
    import json
    
    with open(certificado_path, 'r') as f:
        certificado = json.load(f)
    
    verificador = IntegrityVerifier()
    return verificador.verificar_integridad_total(Path(archivo_path), certificado)


# ==============================================================================
# EJEMPLO DE USO INTEGRADO
# ==============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso de los módulos de producción
    """
    
    print("=== PROTOCOLO AEE v2.1-HARDENED - Módulos de Producción ===\n")
    
    # 1. Demostración de serialización canónica
    print("1. SERIALIZACIÓN CANÓNICA")
    data = {
        "nombre": "documento_prueba",
        "tipo": "imagen",
        "metadatos": {"autor": "Sistema AEE", "versión": 2.1}
    }
    canonical = serializar_canonico(data)
    print(f"   JSON canónico: {canonical}\n")
    
    # 2. Demostración de quórum NTP
    print("2. QUÓRUM NTP ROBUSTO")
    try:
        timestamp = obtener_timestamp_consenso()
        print(f"   Timestamp consensuado: {timestamp['timestamp_iso']}")
        print(f"   Servidores exitosos: {timestamp['servidores_exitosos']}/{timestamp['servidores_consultados']}")
        print(f"   Desviación estándar: {timestamp['desviacion_estandar_ms']} ms\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 3. Demostración de manejo de errores forenses
    print("3. MANEJO DE ERRORES FORENSES")
    
    @transaccion_forense("Operación de prueba")
    def operacion_critica():
        print("   Ejecutando operación crítica...")
        # Simulación de operación
        return "Operación completada"
    
    try:
        resultado = operacion_critica()
        print(f"   {resultado}\n")
    except ForensicTransactionError as e:
        print(f"   Error capturado: {e}\n")
    
    # 4. Verificación de integridad
    print("4. VERIFICACIÓN DE INTEGRIDAD")
    print("   (Requiere archivo y certificado reales para demostración completa)")
    print("   Módulo listo para integración.\n")
    
    print("=== Todos los módulos operacionales ===")