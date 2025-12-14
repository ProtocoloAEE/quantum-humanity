import numpy as np
from typing import Dict, Any

class AEEAdvancedClient:
    def __init__(self, user_id: int, strength: float = 0.5):
        self.user_id = user_id
        self.strength = strength
        
        # Dos thresholds
        self.threshold_low = 0.075   # Alto recall, FPR ~2%
        self.threshold_high = 0.115  # Alta precisión, FPR ~0.1%
        
        # Generar dirección
        np.random.seed(user_id)
        self.direction = np.random.randn(768)
        self.direction = self.direction / np.linalg.norm(self.direction)
    
    def watermark(self, embedding: np.ndarray) -> tuple:
        """Inyecta marca de agua"""
        # Normalizar
        norm = np.linalg.norm(embedding)
        if abs(norm - 1.0) > 1e-6:
            embedding = embedding / norm
        
        # Inyectar
        watermarked = embedding + self.strength * self.direction
        
        # Metadata
        metadata = {
            'user_id': self.user_id,
            'strength': self.strength,
            'hash': hashlib.sha256(watermarked.tobytes()).hexdigest()[:8]
        }
        
        return watermarked, metadata
    
    def verify(self, test_vector: np.ndarray) -> Dict[str, Any]:
        """Verificación de dos etapas"""
        # Normalizar
        test_norm = test_vector / np.linalg.norm(test_vector)
        
        # Correlación
        correlation = np.abs(np.dot(test_norm, self.direction))
        
        # Dos etapas
        if correlation > self.threshold_high:
            return {
                'verified': True,
                'confidence': 'HIGH',
                'score': float(correlation),
                'fpr_estimate': 0.001  # ~0.1%
            }
        elif correlation > self.threshold_low:
            return {
                'verified': True,
                'confidence': 'LOW',
                'score': float(correlation),
                'fpr_estimate': 0.02,  # ~2%
                'note': 'Requires manual review or additional evidence'
            }
        else:
            return {
                'verified': False,
                'score': float(correlation)
            }