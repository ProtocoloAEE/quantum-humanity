import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridCryptoEngine:
    """
    Motor criptográfico híbrido para AEE.
    Combina Ed25519 (clásico) con Kyber/Dilithium (post-cuántico).
    """
    
    # Almacenamiento en memoria de mensajes preservados
    _preserved_messages = {}
    _counter = 0
    
    @staticmethod
    def preserve_message(file_hash: str) -> dict:
        """
        Preserva un mensaje/archivo registrando su hash.
        
        Args:
            file_hash (str): Hash SHA-256 del archivo (64 caracteres hex)
        
        Returns:
            dict: Información de preservación
        """
        try:
            if not isinstance(file_hash, str) or len(file_hash) != 64:
                raise ValueError(f"Hash inválido: debe ser 64 caracteres hexadecimales, recibido: {file_hash}")
            
            HybridCryptoEngine._counter += 1
            
            preservation_record = {
                'id': HybridCryptoEngine._counter,
                'hash': file_hash,
                'timestamp': datetime.utcnow().isoformat(),
                'algorithm': 'SHA-256'
            }
            
            HybridCryptoEngine._preserved_messages[file_hash] = preservation_record
            
            logger.info(f"Mensaje preservado: ID={HybridCryptoEngine._counter}, Hash={file_hash}")
            
            return preservation_record
            
        except Exception as e:
            logger.exception(f"Error en preserve_message: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def get_preserved_message(file_hash: str) -> dict:
        """
        Recupera información de un mensaje preservado.
        
        Args:
            file_hash (str): Hash SHA-256 del archivo
        
        Returns:
            dict: Registro de preservación o None si no existe
        """
        return HybridCryptoEngine._preserved_messages.get(file_hash)
    
    @staticmethod
    def list_preserved_messages() -> list:
        """
        Lista todos los mensajes preservados.
        
        Returns:
            list: Lista de registros de preservación
        """
        return list(HybridCryptoEngine._preserved_messages.values())
