import numpy as np
from aeeprotocol.sdk.client import AEEClient

def run_noise_torture_test():
    print("\n🔥 AEE PROTOCOL v8 - PRUEBA DE RESILIENCIA (RUIDO GAUSSIANO)")
    print("===========================================================")
    print("Objetivo: Demostrar supervivencia a >20% de corrupción de datos.\n")

    # 1. Configuración de Alta Resistencia
    # Aumentamos la fuerza a 0.50 para garantizar robustez extrema
    STRENGTH = 0.50
    user_id = 35664619
    
    print(f"⚙️  Configuración del Motor:")
    print(f"   - User ID: {user_id}")
    print(f"   - Fuerza de Inyección (Strength): {STRENGTH}")
    
    client = AEEClient(user_id=user_id, strength=STRENGTH)
    
    # Umbral interno (Threshold)
    current_threshold = client.engine.threshold
    print(f"   - Umbral de Detección: {current_threshold:.4f}\n")

    # 2. Generación del Vector Base
    dim = 768
    original = np.random.randn(dim).astype(np.float32)
    original /= np.linalg.norm(original)

    # 3. Inyección
    marked, proof = client.watermark(original)
    print(f"✅ Vector Original Marcado (Hash: {proof['hash']})")
    print("-----------------------------------------------------------")

    # 4. El Ataque (Niveles de Ruido)
    # Probamos niveles crecientes de destrucción de datos
    noise_levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

    results = []

    for level in noise_levels:
        noise_pct = int(level * 100)
        print(f"\n⚔️  ATAQUE: Ruido al {noise_pct}%")

        # Generar ruido gaussiano
        noise = np.random.normal(0, level, dim).astype(np.float32)
        
        # Aplicar ataque (Suma vectorial)
        attacked_vec = marked + noise
        
        # Renormalizar (simulando comportamiento de DB vectorial como Pinecone)
        attacked_vec /= np.linalg.norm(attacked_vec)

        # Verificar si la marca sobrevivió
        verification = client.verify(attacked_vec)
        score = verification['confidence_score']
        is_verified = verification['verified']

        # Resultado visual
        status_icon = "🛡️ SOBREVIVIÓ" if is_verified else "❌ ROTO"
        print(f"   Resultado: {status_icon}")
        print(f"   Score: {score:.4f} (vs Umbral: {current_threshold:.4f})")
        
        results.append((noise_pct, is_verified))

    # 5. Resumen Final
    print("\n===========================================================")
    print("📊 RESUMEN FINAL DE RESILIENCIA")
    print("===========================================================")
    passed_20 = False
    for pct, survived in results:
        check = "✅" if survived else "❌"
        print(f"Ruido {pct}%: {check}")
        if pct == 20 and survived:
            passed_20 = True

    print("-----------------------------------------------------------")
    if passed_20:
        print("🏆 CONCLUSIÓN: El protocolo CUMPLE la promesa de resistencia al 20%.")
        print("   (La marca es recuperable incluso con 1/5 del vector destruido)")
    else:
        print("⚠️ CONCLUSIÓN: Se requiere ajustar parámetros.")

if __name__ == "__main__":
    run_noise_torture_test()