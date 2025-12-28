import numpy as np
import os
import hmac
import hashlib

# El modelo de cliente seguro soporta la criptografía HMAC para la semilla.
class AEEClientSecure:
    def __init__(self, user_id, strength=0.5):
        """
        Inicializa el cliente con el ID de usuario y la fuerza del watermark.
        """
        self.user_id = user_id
        self.strength = strength

    def _get_hmac_seed(self, offset=0):
        """
        Genera una semilla HMAC única basada en USER_ID y un offset (Fibonacci).
        Esto permite generar K semillas distintas para el marcaje holográfico (v0.3).
        """
        # La clave secreta debe ser leída de la variable de entorno,
        # pero usamos una clave por defecto para pruebas si no se encuentra.
        key_str = os.environ.get('AEE_SECRET_KEY', 'clave_secreta_default_para_test')
        key = key_str.encode('utf-8')
        
        # Combinamos el USER_ID con el offset de Fibonacci (la posición del patrón)
        message = f"{self.user_id}:{offset}".encode('utf-8')
        
        # Generamos el hash (semilla)
        hmac_generator = hmac.new(key, message, hashlib.sha256)
        return hmac_generator.digest()

    def watermark(self, embedding):
        """
        [DEPRECADO en V0.3 - Esta función ahora se simula en test_resilience.py]
        Marca el embedding con un patrón de ruido único. 
        En la v0.2.5, el offset era 0 (un solo patrón).
        """
        seed_hash = self._get_hmac_seed(offset=0) # Usa offset 0 para compatibilidad con V0.2.5
        
        # Generación del patrón de ruido (como en la v0.2.5)
        np.random.seed(int.from_bytes(seed_hash[:4], 'big'))
        noise_pattern = np.random.normal(0, 1, embedding.shape)
        noise_pattern = noise_pattern / np.linalg.norm(noise_pattern)
        
        marked_embedding = embedding + self.strength * noise_pattern
        
        # La prueba de la V0.3 usa una función custom para el marcaje holográfico.
        # Esta función de cliente se mantiene para estructura.
        return marked_embedding, seed_hash
    
    def verify(self, embedding_atacado):
        """
        [DEPRECADO en V0.3 - Esta función ahora se simula en test_resilience.py]
        Verifica la presencia del watermark (solo el patrón único de la v0.2.5).
        """
        # Simula la verificación del patrón único (offset=0)
        seed_hash = self._get_hmac_seed(offset=0)
        
        np.random.seed(int.from_bytes(seed_hash[:4], 'big'))
        noise_pattern = np.random.normal(0, 1, embedding_atacado.shape)
        noise_pattern = noise_pattern / np.linalg.norm(noise_pattern)
        
        correlation = np.dot(embedding_atacado, noise_pattern)
        
        # La confianza es una simplificación: 0.5 (base) + 0.5 * correlación * fuerza
        confianza = 0.5 + 0.5 * correlation * self.strength
        
        # Umbral simplificado: verificado si la confianza es superior a 0.55
        verified = confianza > 0.55
        
        return {'verified': verified, 'confidence': confianza}