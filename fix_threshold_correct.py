import numpy as np
import hashlib
from scipy import stats

class AEEFixedEngine:
    """
    Motor CORREGIDO con threshold matemáticamente correcto
    """
    
    def __init__(self, strength: float = 0.5, target_fpr: float = 0.02):
        """
        Args:
            strength: Intensidad de la marca (0.3-0.7 recomendado)
            target_fpr: FPR deseado (ej: 0.02 para 2%, 0.001 para 0.1%)
        """
        self.strength = strength
        
        # Threshold calculado CORRECTAMENTE
        dim = 768  # Dimensiones de embedding
        
        # Percentil de distribución normal
        # Para FPR=α, necesitamos P(|Z| > z) = α
        # donde Z ~ N(0, 1/√(n-3))
        z_score = stats.norm.ppf(1 - target_fpr/2)
        self.threshold = z_score / np.sqrt(dim - 3)
        
        print(f"Configuración corregida:")
        print(f"  Strength: {strength}")
        print(f"  Target FPR: {target_fpr:.3%}")
        print(f"  Threshold calculado: {self.threshold:.6f}")
        print(f"  (Anterior: 0.075, diferencia: {self.threshold-0.075:.6f})")
        print(f"  Nota: Correlación ∈ [0,1], threshold debe ser < 1.0")
    
    def compute_direction(self, user_id: int) -> np.ndarray:
        """Dirección NORMALIZADA (norma = 1.0 exacta)"""
        seed_bytes = str(user_id).encode()
        seed_int = int(hashlib.sha256(seed_bytes).hexdigest()[:8], 16)
        
        np.random.seed(seed_int)
        direction = np.random.randn(768)
        
        # Normalización PRECISA
        norm = np.linalg.norm(direction)
        if norm < 1e-10:
            direction = np.ones(768) / np.sqrt(768)
        else:
            direction = direction / norm
        
        return direction
    
    def inject(self, embedding: np.ndarray, user_id: int):
        """Inyección CORRECTA"""
        # 1. Normalizar embedding de entrada
        norm_in = np.linalg.norm(embedding)
        if abs(norm_in - 1.0) > 1e-6:
            embedding = embedding / norm_in
        
        # 2. Obtener dirección normalizada
        direction = self.compute_direction(user_id)
        
        # 3. Inyectar
        watermarked = embedding + self.strength * direction
        
        # 4. Normalizar salida
        watermarked = watermarked / np.linalg.norm(watermarked)
        
        return watermarked
    
    def detect(self, test_vector: np.ndarray, user_id: int):
        """Detección CORRECTA"""
        # 1. Normalizar vector de prueba
        norm_test = np.linalg.norm(test_vector)
        if abs(norm_test - 1.0) > 1e-6:
            test_vector = test_vector / norm_test
        
        # 2. Obtener MISMA dirección
        direction = self.compute_direction(user_id)
        
        # 3. Calcular score (correlación absoluta)
        score = np.abs(np.dot(test_vector, direction))
        
        # 4. Decidir
        detected = score > self.threshold
        
        return {
            'detected': detected,
            'score': float(score),
            'threshold': float(self.threshold),
            'strength': float(self.strength)
        }

# ============================================================
# TEST DE VALIDACIÓN
# ============================================================

def test_fixed_engine_correct():
    print("\n" + "="*60)
    print("TEST DEL MOTOR CORREGIDO (VERSIÓN MATEMÁTICAMENTE CORRECTA)")
    print("="*60)
    
    # Prueba múltiples FPRs
    test_cases = [
        {'target_fpr': 0.02, 'strength': 0.5, 'name': '2% FPR'},
        {'target_fpr': 0.01, 'strength': 0.5, 'name': '1% FPR'},
        {'target_fpr': 0.001, 'strength': 0.5, 'name': '0.1% FPR'},
        {'target_fpr': 0.02, 'strength': 0.4, 'name': '2% FPR, strength=0.4'},
    ]
    
    for case in test_cases:
        print(f"\n{'='*40}")
        print(f"Test: {case['name']}")
        print(f"{'='*40}")
        
        user_id = 123456
        engine = AEEFixedEngine(
            strength=case['strength'], 
            target_fpr=case['target_fpr']
        )
        
        # 1. Test FPR
        print(f"\n1. Test FPR (target={case['target_fpr']:.2%}):")
        n_tests = 5000
        false_positives = 0
        
        for i in range(n_tests):
            random_vec = np.random.randn(768)
            random_vec = random_vec / np.linalg.norm(random_vec)
            
            result = engine.detect(random_vec, user_id)
            if result['detected']:
                false_positives += 1
        
        observed_fpr = false_positives / n_tests
        print(f"   Target FPR: {case['target_fpr']:.3%}")
        print(f"   Observed FPR: {observed_fpr:.3%}")
        print(f"   Difference: {observed_fpr-case['target_fpr']:.4%}")
        
        # 2. Test TPR (true positive)
        print(f"\n2. Test TPR (watermarked vector):")
        original = np.random.randn(768)
        original = original / np.linalg.norm(original)
        
        watermarked = engine.inject(original, user_id)
        result = engine.detect(watermarked, user_id)
        
        print(f"   Detected: {result['detected']}")
        print(f"   Score: {result['score']:.6f}")
        print(f"   Threshold: {result['threshold']:.6f}")
        print(f"   Margin: {result['score']-result['threshold']:.6f}")
        
        # 3. Score sin marca (baseline)
        result_original = engine.detect(original, user_id)
        print(f"   Original (no watermark) score: {result_original['score']:.6f}")
    
    # 4. Tabla de thresholds por FPR
    print(f"\n{'='*60}")
    print("TABLA: Thresholds para diferentes FPRs (dim=768)")
    print(f"{'='*60}")
    print(f"{'FPR Target':<12} {'z-score':<10} {'Threshold':<12}")
    print(f"{'-'*40}")
    
    dim = 768
    for fpr in [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.001]:
        z = stats.norm.ppf(1 - fpr/2)
        threshold = z / np.sqrt(dim - 3)
        print(f"{fpr:>7.3%}     {z:>8.4f}   {threshold:>10.6f}")
    
    print(f"\nNota: Tu threshold actual 0.075 corresponde a FPR ≈ {2*(1-stats.norm.cdf(0.075*np.sqrt(765))):.3%}")

if __name__ == "__main__":
    test_fixed_engine_correct()