import numpy as np
from aeeprotocol.sdk.client import AEEClient

print("="*60)
print("DEBUG: ¿Qué threshold usas REALMENTE?")
print("="*60)

# 1. Mira tu código client.py
print("\n1. Revisando client.py...")
with open('aeeprotocol/sdk/client.py', 'r') as f:
    content = f.read()
    if 'threshold' in content:
        print("   Encontrado 'threshold' en client.py")
        lines = [l for l in content.split('\n') if 'threshold' in l]
        for line in lines[:5]:  # Primeras 5 ocurrencias
            print(f"   → {line.strip()}")
    else:
        print("   No encontrado 'threshold' en client.py")

# 2. Crea cliente y verifica
print("\n2. Creando cliente con strength=0.5...")
client = AEEClient(user_id=123, strength=0.5)

# 3. Test práctico
print("\n3. Test práctico de threshold:")
original = np.random.randn(768).astype('float32')
original = original / np.linalg.norm(original)

marked, _ = client.watermark(original)

# Verificar con vector aleatorio (debería dar ~3.8% detecciones si threshold=0.075)
n_tests = 1000
detections = 0
scores = []

for i in range(n_tests):
    random_vec = np.random.randn(768).astype('float32')
    random_vec = random_vec / np.linalg.norm(random_vec)
    
    result = client.verify(random_vec)
    if result['verified']:
        detections += 1
    scores.append(result.get('confidence_score', 0))

print(f"   Tests con vectores aleatorios: {detections}/{n_tests}")
print(f"   FPR observado: {detections/n_tests:.4%}")
print(f"   Scores min/max: {min(scores):.4f}/{max(scores):.4f}")

# 4. ¿Cuál es el threshold REAL?
print("\n4. Calculando threshold efectivo...")
# Ordenar scores y encontrar percentil 96.2 (100% - 3.8%)
sorted_scores = np.sort(scores)
if len(sorted_scores) > 0:
    idx_96 = int(0.962 * len(sorted_scores))
    effective_threshold = sorted_scores[idx_96] if idx_96 < len(sorted_scores) else sorted_scores[-1]
    print(f"   Para FPR=3.8%, threshold debería ser: {effective_threshold:.6f}")
    print(f"   Threshold reportado: 0.075000")
    print(f"   Diferencia: {abs(effective_threshold - 0.075):.6f}")