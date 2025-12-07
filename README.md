# AEE Protocol v8
## Vector Traceability for the AI Era

**Protect your embeddings. Prove your ownership. Maintain compliance.**

AEE (Attribution & Evidence for Embeddings) is an open-source protocol for invisible watermarking of vector embeddings, with blockchain certification for legal proof. Survives 20% noise, <1% FP rate (10k tests).

### Quick Start
```python
pip install aeeprotocol  # Día 2

from aeeprotocol import AEEv8
aee = AEEv8(user_id=35664619)  # Tu DNI soberano

embedding = np.random.randn(768) / np.linalg.norm(np.random.randn(768))
marked, proof = aee.inject(embedding)
detection = aee.detect(marked)
print(f"Detected: {detection['detected']}, Confidence: {detection['confidence']}")