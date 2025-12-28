"""
AEE Protocol - Torture Test contra Llama 2 Local
Valida que el watermark sobrevive a reescrituras de IA
VERSION MEJORADA: strength=0.50 + embeddings multilingües
"""

import numpy as np
import json
import requests
from datetime import datetime
from aeeprotocol.core.engine import AEEMathEngine
from sentence_transformers import SentenceTransformer

print("🔥 AEE PROTOCOL - TORTURE TEST LLAMA (MEJORADO)\n")

# =====================================================
# CONFIGURACIÓN MEJORADA
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama2:7b"
EMBEDDING_MODEL = "sentence-transformers/multilingual-MiniLM-L12-v2"  # Multilingüe
STRENGTH = 0.50  # Máxima robustez

print(f"Configuración:")
print(f"  - Ollama: {OLLAMA_URL}")
print(f"  - Modelo: {MODEL_NAME}")
print(f"  - Embeddings: {EMBEDDING_MODEL} (multilingüe)")
print(f"  - Strength: {STRENGTH}\n")

# =====================================================
# INICIALIZAR
# =====================================================

print("📥 Cargando modelo de embeddings multilingüe...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✓ Embeddings cargado (dimensión: 384)\n")

engine = AEEMathEngine(strength=STRENGTH)
print(f"✓ Engine AEE inicializado (strength: {engine.strength}, threshold: {engine.threshold:.4f})\n")

# =====================================================
# TEXTOS DE PRUEBA
# =====================================================

test_texts = [
    "El watermarking vectorial es una técnica criptográfica para proteger embeddings de inteligencia artificial de uso no autorizado.",
    "Los embeddings son representaciones numéricas de texto en espacios vectoriales de alta dimensión que capturan significado semántico.",
    "La trazabilidad de datos es crítica en auditorías de modelos de lenguaje para verificar conformidad con regulaciones."
]

results = {
    'timestamp': datetime.now().isoformat(),
    'model': MODEL_NAME,
    'embedding_model': EMBEDDING_MODEL,
    'strength': engine.strength,
    'threshold': engine.threshold,
    'tests': [],
    'summary': {}
}

# =====================================================
# TORTURE TEST
# =====================================================

print("="*70)
print("🔥 INICIANDO TORTURE TEST (VERSIÓN MEJORADA)")
print("="*70)
print(f"Textos: {len(test_texts)}")
print(f"Reescrituras por texto: 3")
print(f"Total de tests: {len(test_texts) * 3}\n")

watermarks_survived = 0
total_tests = 0

for text_idx, original_text in enumerate(test_texts, 1):
    print(f"\n{'─'*70}")
    print(f"TEXTO {text_idx}: {original_text[:60]}...")
    print(f"{'─'*70}")
    
    # Step 1: Embedding original
    print(f"\n[1/4] Generando embedding original...")
    original_embedding = embedding_model.encode(original_text)
    original_embedding = original_embedding / np.linalg.norm(original_embedding)
    print(f"      ✓ Embedding: {original_embedding.shape}")
    
    # Step 2: Watermark
    print(f"[2/4] Inyectando watermark...")
    marked_embedding, metadata = engine.inject(original_embedding, user_id=35664619)
    initial_detection = engine.detect(marked_embedding, user_id=35664619)
    print(f"      ✓ Watermark inyectado")
    print(f"      ✓ Similitud inicial: {initial_detection:.4f} (threshold: {engine.threshold:.4f})")
    
    # Step 3: Reescrituras
    rewrite_prompts = [
        f"Reescribe esta frase de forma más clara y concisa: {original_text}",
        f"Parafrasea manteniendo exactamente el significado: {original_text}",
        f"Expresa la misma idea con otras palabras pero sin perder contenido: {original_text}"
    ]
    
    for iter_num, prompt in enumerate(rewrite_prompts, 1):
        print(f"\n   [ITERACIÓN {iter_num}/3]")
        print(f"   [3/4] Reescribiendo con Llama...")
        
        try:
            # Llamar a Ollama
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 120
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"       ❌ Error Ollama: {response.status_code}")
                continue
            
            rewritten_text = response.json()['response'].strip()
            print(f"       Original: {original_text[:50]}...")
            print(f"       Reescrito: {rewritten_text[:50]}...")
            
            # Step 4: Embedding reescrito
            print(f"   [4/4] Obteniendo embedding reescrito...")
            rewritten_embedding = embedding_model.encode(rewritten_text)
            rewritten_embedding = rewritten_embedding / np.linalg.norm(rewritten_embedding)
            
            # Detectar watermark
            detection_score = engine.detect(rewritten_embedding, user_id=35664619)
            detected = detection_score > engine.threshold
            
            total_tests += 1
            if detected:
                watermarks_survived += 1
                status = "✅ SOBREVIVIÓ"
            else:
                status = "❌ PERDIDO"
            
            print(f"       {status}")
            print(f"       Similitud: {detection_score:.4f}")
            
            results['tests'].append({
                'text_idx': text_idx,
                'iteration': iter_num,
                'original': original_text,
                'rewritten': rewritten_text,
                'detected': detected,
                'similarity': float(detection_score),
                'threshold': float(engine.threshold)
            })
        
        except requests.exceptions.ConnectionError:
            print(f"       ❌ Error: No puedo conectar a Ollama")
            print(f"          ¿Ollama está corriendo en {OLLAMA_URL}?")
            break
        except Exception as e:
            print(f"       ❌ Error: {e}")

# =====================================================
# RESUMEN
# =====================================================

print(f"\n\n{'='*70}")
print("📊 RESUMEN DE TORTURE TEST")
print(f"{'='*70}")

if total_tests > 0:
    survival_rate = watermarks_survived / total_tests
    results['summary'] = {
        'total_tests': total_tests,
        'watermarks_survived': watermarks_survived,
        'watermarks_lost': total_tests - watermarks_survived,
        'survival_rate': float(survival_rate)
    }
    
    print(f"Total de tests: {total_tests}")
    print(f"Watermarks sobrevivieron: {watermarks_survived}")
    print(f"Watermarks perdidos: {total_tests - watermarks_survived}")
    print(f"Tasa de supervivencia: {survival_rate:.1%}")
    
    if survival_rate > 0.8:
        print(f"\n✅ RESULTADO: PROTOCOLO ROBUSTO")
    elif survival_rate > 0.5:
        print(f"\n⚠️  RESULTADO: PROTOCOLO MODERADO - Buenas bases pero mejora posible")
    else:
        print(f"\n❌ RESULTADO: PROTOCOLO DÉBIL - Necesita mejoras significativas")
else:
    print("❌ No se ejecutaron tests (posiblemente error de conexión)")

# Guardar resultados
output_file = f"torture_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Resultados guardados en: {output_file}")
print(f"\n✅ Torture test completado")