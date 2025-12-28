try:
    from aeeprotocol.sdk.client import AEEClient
    import numpy as np
    
    print("--- AUDITORIA DE AGENTE PROFESIONAL ---")
    client = AEEClient()
    print(client.create_identity())
    
    dummy_data = np.random.rand(1536)
    seal = client.sign_data(dummy_data)
    
    print(f"OK: Sello generado ({seal['algorithm']})")
    print("SUCCESS: ESTRUCTURA VALIDADA Y CORREGIDA")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
