import numpy as np
from aeeprotocol.sdk.client import AEEClient

print("="*70)
print("🔬 AUDITORÍA ESTADÍSTICA RIGUROSA - AEE PROTOCOL")
print("="*70)

# Configuración
user_id = 35664619
dim = 768
strength = 0.50
n_vectors = 50  # Múltiples vectores
n_trials_per_noise = 100  # Múltiples ensayos por vector

# Niveles de ruido a probar
noise_levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

print(f"\nConfiguración:")
print(f"  Vectores: {n_vectors}")
print(f"  Ensayos por vector por ruido: {n_trials_per_noise}")
print(f"  Total ensayos por ruido: {n_vectors * n_trials_per_noise}")
print(f"  Dimensión: {dim}")
print(f"  Strength: {strength}\n")

# Guardar todos los scores para análisis
all_results = {}

for noise_level in noise_levels:
    print(f"\n{'─'*70}")
    print(f"PRUEBA CON RUIDO σ = {noise_level:.2f}")
    print(f"{'─'*70}")
    
    detection_counts = []
    all_scores = []
    
    # Múltiples vectores
    for vec_idx in range(n_vectors):
        # Vector original NUEVO cada vez
        original = np.random.randn(dim).astype(np.float32)
        original = original / np.linalg.norm(original)
        
        # Marcar
        client = AEEClient(user_id=user_id, strength=strength)
        marked, proof = client.watermark(original)
        
        vec_detections = 0
        vec_scores = []
        
        # Múltiples ensayos CON RUIDO
        for trial in range(n_trials_per_noise):
            # Ruido DIFERENTE cada ensayo
            noise = np.random.normal(0, noise_level, dim).astype(np.float32)
            attacked = marked + noise
            attacked = attacked / np.linalg.norm(attacked)
            
            # Detectar
            result = client.verify(attacked)
            score = result['confidence_score']
            
            vec_scores.append(score)
            all_scores.append(score)
            
            if result['verified']:
                vec_detections += 1
        
        detection_counts.append(vec_detections)
    
    # Estadísticas
    survival_rates = [count/n_trials_per_noise for count in detection_counts]
    mean_survival = np.mean(survival_rates)
    std_survival = np.std(survival_rates)
    
    print(f"\nPor Vector (n={n_vectors}):")
    print(f"  Tasa detección promedio: {mean_survival:.1%}")
    print(f"  Std dev: {std_survival:.4f}")
    print(f"  Min detección: {np.min(survival_rates):.1%}")
    print(f"  Max detección: {np.max(survival_rates):.1%}")
    
    print(f"\nScores Agregados (n={len(all_scores)}):")
    print(f"  Score promedio: {np.mean(all_scores):.6f}")
    print(f"  Score std dev: {np.std(all_scores):.6f}")
    print(f"  Score min: {np.min(all_scores):.6f}")
    print(f"  Score max: {np.max(all_scores):.6f}")
    print(f"  Threshold (0.075): {'✅ PASA' if np.mean(all_scores) > 0.075 else '❌ FALLA'}")
    
    all_results[noise_level] = {
        'mean_survival': mean_survival,
        'std_survival': std_survival,
        'mean_score': np.mean(all_scores),
        'std_score': np.std(all_scores),
        'scores': all_scores
    }

# FPR test (vectores SIN watermark)
print(f"\n{'='*70}")
print("🔍 TEST DE FALSOS POSITIVOS (FPR)")
print(f"{'='*70}")

fpr_tests = 10000
fpr_positives = 0
fpr_scores = []

client = AEEClient(user_id=user_id, strength=strength)

for _ in range(fpr_tests):
    # Vector COMPLETAMENTE aleatorio (sin marca)
    random_vec = np.random.randn(dim).astype(np.float32)
    random_vec = random_vec / np.linalg.norm(random_vec)
    
    # Verificar (debería FALLAR porque no hay marca)
    result = client.verify(random_vec)
    score = result['confidence_score']
    fpr_scores.append(score)
    
    if result['verified']:
        fpr_positives += 1

fpr = fpr_positives / fpr_tests

print(f"\nFPR Observado: {fpr:.4%} ({fpr_positives}/{fpr_tests})")
print(f"FPR Esperado (gaussiano i.i.d): ~{2.3/np.sqrt(dim):.4%}")

if fpr > 0.01:
    print(f"⚠️  FPR ALTO: {fpr:.4%} es inaceptable (debería ser <0.1%)")
else:
    print(f"✓ FPR aceptable")

# Resumen final
print(f"\n{'='*70}")
print("📊 RESUMEN FINAL")
print(f"{'='*70}\n")

for noise_level in noise_levels:
    result = all_results[noise_level]
    status = "✅" if result['mean_survival'] > 0.5 else "❌"
    print(f"Ruido {noise_level:.2f}: {status} Supervivencia={result['mean_survival']:.1%}, Score={result['mean_score']:.4f}")

print(f"\n✓ Test completado. Datos salvados para análisis.")