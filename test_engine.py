"""
Test simple para AEEMathEngine
"""
import numpy as np
from aeeprotocol.core.engine import AEEMathEngine

print("🔒 TEST: AEE Engine Básico\n")

# Inicializar
engine = AEEMathEngine(strength=0.25)
print(f"✓ Engine inicializado")
print(f"  Strength: {engine.strength}")
print(f"  Threshold: {engine.threshold}\n")

# Test 1: Inyección básica
print("TEST 1: Inyección")
test_embedding = np.random.randn(768).astype("float32")
marked, metadata = engine.inject(test_embedding, user_id=35664619)
print(f"✓ Embedding marcado")
print(f"  Metadatos: {metadata}\n")

# Test 2: Detección
print("TEST 2: Detección")
similarity = engine.detect(marked, user_id=35664619)
print(f"✓ Similitud con marca: {similarity:.4f}")
print(f"  Threshold: {engine.threshold:.4f}")
detected = similarity > engine.threshold
print(f"  ¿Detectado?: {detected}\n")

# Test 3: Resiliencia a ruido 10%
print("TEST 3: Resiliencia a ruido (10%)")
noisy = marked + np.random.randn(768) * 0.1
noisy = noisy / np.linalg.norm(noisy)
similarity_noisy = engine.detect(noisy, user_id=35664619)
detected_noisy = similarity_noisy > engine.threshold
print(f"✓ Similitud tras ruido: {similarity_noisy:.4f}")
print(f"  ¿Detectado?: {detected_noisy}\n")

# Test 4: Falso positivo (embedding aleatorio)
print("TEST 4: Falso positivo")
random_emb = np.random.randn(768).astype("float32")
random_emb = random_emb / np.linalg.norm(random_emb)
similarity_random = engine.detect(random_emb, user_id=35664619)
detected_random = similarity_random > engine.threshold
print(f"✓ Similitud con random: {similarity_random:.4f}")
print(f"  ¿Falso positivo?: {detected_random}\n")

print("✅ Todos los tests completados")