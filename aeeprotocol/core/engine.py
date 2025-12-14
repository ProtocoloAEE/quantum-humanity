import numpy as np
import hashlib
from typing import Tuple, Dict, Optional

class AEEMathEngine:
    """
    Motor matemático puro del Protocolo AEE (Architecture for Embedding Evidence).
    v8.1: Semilla Inmutable para alta resistencia al ruido.
    """
    
    def __init__(self, strength: float = 0.25):
        self.strength = strength
        # Umbral ajustado para alta sensibilidad
        self.threshold = strength * 0.15

    def compute_direction(self, embedding: np.ndarray, user_id: int) -> np.ndarray:
        """
        Genera un vector de dirección basado ÚNICAMENTE en la identidad.
        Esto garantiza que la dirección sea recuperable incluso si el vector está corrupto.
        """
        # 1. Semilla criptográfica INMUTABLE: Hash(UserID)
        # ALERTA: No incluir 'embedding' en la semilla para resistir ataques de ruido
        seed_bytes = str(user_id).encode()
        
        # Usamos SHA256 para máxima entropía
        seed_int = int(hashlib.sha256(seed_bytes).hexdigest()[:8], 16) % (2**32)
        
        # 2. Generación Pseudo-Aleatoria
        rng = np.random.RandomState(seed_int)
        direction = rng.randn(len(embedding))
        
        # 3. Ortogonalización y Normalización
        # Simplemente normalizamos la dirección aleatoria
        direction = direction / np.linalg.norm(direction)
        
        return direction

    def inject(self, embedding: np.ndarray, user_id: int) -> Tuple[np.ndarray, dict]:
        """Aplica la marca de agua."""
        norm = np.linalg.norm(embedding)
        base_emb = embedding / norm if abs(norm - 1.0) > 0.01 else embedding
        
        # Calcular dirección maestra
        direction = self.compute_direction(base_emb, user_id)
        
        # Inyección: V + alpha * D
        watermarked = base_emb + self.strength * direction
        
        meta = {
            'algo': 'AEEv8.1-Robust',
            'strength': self.strength,
            'hash': hashlib.sha256(watermarked.tobytes()).hexdigest()[:8]
        }
        return watermarked, meta

    def detect(self, embedding: np.ndarray, user_id: int) -> float:
        """Detecta la marca incluso con ruido."""
        embedding_norm = embedding / np.linalg.norm(embedding)
        
        # Recuperamos la misma dirección maestra usando solo el ID
        direction = self.compute_direction(embedding_norm, user_id)
        
        return float(np.dot(embedding_norm, direction))