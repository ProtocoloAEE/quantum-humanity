# test_aee_v8.py
import pytest
import numpy as np
from aee_v8 import AEEv8, LegalCertification, AEEv8Legal  # Ajusta import si necesario

def test_aee_initialization():
    aee = AEEv8(user_id=12345, auto_calibrate=False)
    assert aee.user_id == 12345
    assert 0.1 <= aee.strength <= 0.5
    assert aee.VERSION == "8.0.0"

def test_injection_deterministic():
    aee = AEEv8(user_id=999, auto_calibrate=False)
    embedding = np.random.randn(768)
    embedding = embedding / np.linalg.norm(embedding)
   
    marked1, meta1 = aee.inject(embedding)
    marked2, meta2 = aee.inject(embedding)
   
    # Debería ser determinista
    assert np.allclose(marked1, marked2)
    assert meta1['embedding_hash'] == meta2['embedding_hash']

def test_detection_positive():
    aee = AEEv8(user_id=777, auto_calibrate=False)
    embedding = np.random.randn(512)
    embedding = embedding / np.linalg.norm(embedding)
   
    marked, _ = aee.inject(embedding)
    detection = aee.detect(marked)
   
    assert detection['detected'] == True
    assert detection['confidence'] > 0.5

def test_detection_negative():
    aee = AEEv8(user_id=888, auto_calibrate=False)
    # Embedding aleatorio sin marca
    random_embedding = np.random.randn(768)
    random_embedding = random_embedding / np.linalg.norm(random_embedding)
   
    detection = aee.detect(random_embedding, fast_mode=True)
    # No debería detectar marca
    assert detection['detected'] == False

def test_batch_processing():
    aee = AEEv8(user_id=111, auto_calibrate=False)
    embeddings = [np.random.randn(256) for _ in range(10)]
    embeddings = [e / np.linalg.norm(e) for e in embeddings]
   
    results = aee.batch_process(embeddings, operation='detect')
    assert len(results) == 10
    assert all('detected' in r for r in results)

def test_legal_certification():
    legal = LegalCertification()
    test_data = {"test": "data", "timestamp": "2024-01-01"}
   
    proof = legal.create_timestamp_proof(test_data)
    assert 'proof_id' in proof
    assert 'timestamp' in proof
    assert 'data_hash' in proof
   
    verification = legal.verify_proof(proof, test_data)
    assert 'hash_valid' in verification
    assert 'timestamp_valid' in verification

@pytest.mark.asyncio
async def test_fastapi_endpoints():
    # Test de endpoints (simplificado)
    from fastapi.testclient import TestClient
    from main import app  # Ajusta si main.py es el API
   
    client = TestClient(app)
   
    # Test root
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()
   
    # Test health
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])