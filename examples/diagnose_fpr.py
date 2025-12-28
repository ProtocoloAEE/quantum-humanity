import numpy as np
from scipy import stats

def diagnose_why_high_fpr():
    """Descubre por qué tu FPR es 1.98% y no 0.07%"""
    
    dim = 768
    threshold = 0.075
    
    print("="*60)
    print("DIAGNÓSTICO DE FPR ALTO")
    print("="*60)
    
    # 1. FPR teórico
    z_theory = threshold * np.sqrt(dim - 3)
    fpr_theory = 2 * (1 - stats.norm.cdf(z_theory))
    print(f"\n1. FPR TEÓRICO (768D, threshold={threshold}):")
    print(f"   z = {z_theory:.4f}")
    print(f"   FPR = {fpr_theory:.6f} ({fpr_theory:.4%})")
    
    # 2. Simulación simple
    print(f"\n2. SIMULACIÓN DIRECTA:")
    n_trials = 10000
    false_positives = 0
    
    for i in range(n_trials):
        # Dos vectores aleatorios independientes
        v1 = np.random.randn(dim)
        v2 = np.random.randn(dim)
        
        # Normalizar (como debería hacer tu código)
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        
        # Correlación absoluta
        corr = np.abs(np.dot(v1, v2))
        
        if corr > threshold:
            false_positives += 1
    
    fpr_sim = false_positives / n_trials
    print(f"   FPR simulado: {fpr_sim:.4f} ({fpr_sim:.4%})")
    print(f"   Diferencia vs teórico: {fpr_sim - fpr_theory:.6f}")
    
    # 3. ¿Qué pasa si NO normalizas?
    print(f"\n3. SIN NORMALIZAR (¿es tu bug?):")
    false_positives_no_norm = 0
    
    for i in range(n_trials):
        v1 = np.random.randn(dim)  # No normalizado
        v2 = np.random.randn(dim)  # No normalizado
        
        # Correlación sin normalizar
        corr = np.abs(np.dot(v1, v2))
        # ¡Esto puede ser cualquier número!
        
        # Normalizar después (simulando error común)
        norm_factor = np.linalg.norm(v1) * np.linalg.norm(v2)
        corr_normalized = corr / norm_factor if norm_factor > 0 else 0
        
        if corr_normalized > threshold:
            false_positives_no_norm += 1
    
    fpr_no_norm = false_positives_no_norm / n_trials
    print(f"   FPR sin normalizar bien: {fpr_no_norm:.4f} ({fpr_no_norm:.4%})")
    
    # 4. Recomendación
    print(f"\n4. DIAGNÓSTICO PROBABLE:")
    if abs(fpr_sim - fpr_theory) < 0.001:
        print("   ✓ Tu simulación concuerda con teoría")
        print("   → El problema está en TU implementación real")
    elif abs(fpr_no_norm - 0.0198) < 0.001:
        print("   ✗ ¡ENCONTRADO! No estás normalizando correctamente")
        print("   → Arregla la normalización en tu código")
    else:
        print("   ? Problema diferente. Revisa:")
        print("     - ¿Threshold calculado diferente?")
        print("     - ¿Usas correlación absoluta?")
        print("     - ¿Los vectores son realmente i.i.d gaussianos?")

if __name__ == "__main__":
    diagnose_why_high_fpr()