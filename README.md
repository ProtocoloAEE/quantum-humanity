# 🔒 AEE Protocol v0.2.5 (Beta)
**Vector Watermarking for AI Embeddings - Engine v8.3**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-beta-yellow)
![Validation](https://img.shields.io/badge/validation-5000%2B%20trials-success)
![Noise Tolerance](https://img.shields.io/badge/noise%20tolerance-20%25-orange)

---

## 🎯 **What is AEE Protocol?**

AEE Protocol is an **open-source watermarking system** for vector embeddings that enables:

- 🔐 **Proof of Ownership** - Cryptographically mark your embeddings
- 🔍 **Data Leakage Detection** - Identify stolen vectors in databases
- 💪 **Noise Resilience** - Survive corruption and transformations
- ⚡ **Zero Performance Impact** - <1ms injection time per vector

**Use Case:** Protect vectorized data in Pinecone, Weaviate, Qdrant from unauthorized use.

---

## ❓ **Why AEE Protocol?**

Vector embeddings are the "oil" of modern AI, but:
- 🔓 **No protection**: Anyone can copy vectors from Pinecone/Weaviate
- ⚖️ **No legal proof**: Impossible to prove ownership in disputes  
- 🔍 **No blind detection**: You need the original to compare

**AEE Protocol solves this mathematically**, not heuristically.

- Watermark survives transformations (noise, compression, quantization)
- Detection works without original vector (blind detection)
- Cryptographic proof for legal disputes

---

## 📊 **Validation Results (5,000+ Independent Trials)**

### Noise Resilience - Real World Performance

| Noise Level | Survival Rate | Mean Score | Recommended Use |
|-------------|---------------|------------|-----------------|
| **σ = 0.05** | 100.0% | 0.2817 | ✅ Perfect - Production ready |
| **σ = 0.10** | 99.6% | 0.1679 | ✅ Excellent - Recommended range |
| **σ = 0.15** | 87.2% | 0.1145 | ✅ Good - Acceptable |
| **σ = 0.20** | 67.3% | 0.0906 | ⚠️ Marginal - Edge of reliability |
| **σ = 0.25** | 45.5% | 0.0714 | ❌ Unreliable - Not recommended |

**Methodology:** Gaussian noise injection, 5,000 independent trials per level.  
**Full details:** See [VALIDATION.md](./VALIDATION.md)

### False Positive Analysis
- **Current FPR:** 1.98% @ threshold 0.075
- **Optimized FPR:** <0.5% @ threshold 0.12 (with TPR tradeoff)
- **Distribution:** Gaussian (as expected from theory)

**Production Recommendation:** Operate at **σ ≤ 0.15** for 87%+ reliability.

---

## ⚠️ **Beta Status & Known Limitations**

### Current Version (v0.2.5)

**Security Notice:**
- Keys are derived deterministically from `user_id` for session persistence
- This mode is **INSECURE for production** - anyone with your `user_id` can detect/remove marks
- Use explicit `secret_key` parameter for real security (see below)

**Known Limitations:**
1. **FPR 1.98%** - High for very large databases (millions of vectors)
2. **Not for AI Attribution** - Cannot detect if AI model was trained on your data
3. **Single Watermark** - Not holographic (v0.3.0 will add redundancy)
4. **Noise Ceiling** - Reliable only up to σ=0.20 (20% noise)

**What it IS good for:**
- ✅ Detecting direct embedding theft from vector databases
- ✅ Proving ownership in legal disputes
- ✅ Auditing data leakage incidents
- ✅ Testing and research purposes

---

## ⚡ **Quick Start**

### Installation

**From source (recommended for beta):**
```bash
git clone https://github.com/ProtocoloAEE/aee-protocol.git
cd aee-protocol
pip install -e .
```

**PyPI (coming in v0.3.0):**
```bash
pip install aeeprotocol  # Not yet available
```

### Basic Usage
```python
from aeeprotocol.sdk.client import AEEClient
import numpy as np

# Initialize with your identity
client = AEEClient(user_id=35664619, strength=0.50)

# 1. Mark your vector
original_vector = np.random.randn(768).astype('float32')
marked_vector, proof = client.watermark(original_vector)

# 2. Later, verify ownership
result = client.verify(marked_vector)
print(f"Ownership verified: {result['verified']}")
print(f"Confidence: {result['confidence_score']:.4f}")
```

### Secure Mode (Production)
```python
import base64

# Generate secure key once
key = AEEClient.generate_key()
# Save this key securely! (password manager, env var, etc.)

# Use it
client = AEEClient(
    user_id=35664619, 
    secret_key=base64.b64decode(key)
)
```

---

## 🔌 **Integrations**

### Pinecone
```python
from pinecone import Pinecone
from aeeprotocol.sdk.client import AEEClient
import numpy as np

# Initialize
pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("protected-index")
client = AEEClient(user_id=35664619)

# Watermark before storing
embedding = np.random.randn(768).astype('float32')
marked_vec, proof = client.watermark(embedding)

index.upsert(vectors=[{
    "id": "vec_1",
    "values": marked_vec.tolist(),
    "metadata": {"aee_proof": proof}
}])

# Audit later
stored_vec = index.fetch("vec_1")["vectors"]["vec_1"]["values"]
result = client.verify(np.array(stored_vec))

if result['verified']:
    print("✅ Your data detected - ownership confirmed")
else:
    print("❌ Not your data")
```

### LangChain
```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from aeeprotocol.sdk.client import AEEClient

client = AEEClient(user_id=35664619)

def secure_ingest(texts, metadatas):
    """Inject watermarks before storage"""
    embeddings = OpenAIEmbeddings()
    raw_vecs = embeddings.embed_documents(texts)
    
    secure_vecs = []
    proofs = []
    for raw in raw_vecs:
        marked, proof = client.watermark(raw)
        secure_vecs.append(marked)
        proofs.append(proof)
    
    # Store with proof metadata
    vectorstore = PineconeVectorStore.from_embeddings(
        embeddings=list(zip(texts, secure_vecs)),
        metadatas=[{**m, "aee_proof": p} for m, p in zip(metadatas, proofs)]
    )
```

### LlamaIndex
```python
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from aeeprotocol.sdk.client import AEEClient

class AEEWrapper:
    """Wrapper that injects watermarks automatically"""
    def __init__(self, model):
        self.model = model
        self.aee_client = AEEClient(user_id=35664619)
    
    def get_text_embedding(self, text):
        raw = self.model.get_text_embedding(text)
        marked, _ = self.aee_client.watermark(raw)
        return marked.tolist()

# Usage
secure_model = AEEWrapper(OpenAIEmbedding())
index = VectorStoreIndex.from_documents(docs, embed_model=secure_model)
```

---

## 🏗️ **How It Works**

### Mathematical Foundation

1. **Deterministic Direction Generation**
   - Seed derived from user credentials
   - Ensures consistency across detections

2. **Orthogonal Watermark Injection**
```
   Watermarked = Original + (strength × Direction)
```
   - Preserves semantic meaning
   - Minimal quality degradation (<2%)

3. **Blind Detection**
   - Regenerate direction from user_id/secret_key
   - Compute correlation score
   - Threshold-based decision

### Architecture
```
┌───────────────────────┐     ┌───────────────────────┐
│   Your Identity       │     │   Vector Database     │
│ (user_id + secret)    │     │ (Pinecone/Weaviate)   │
└──────────┬────────────┘     └──────────▲────────────┘
           │                              │
           ▼                              │
┌───────────────────────┐                │
│   AEE Protocol Core   │────────────────┤
│ (Deterministic Seed)  │   Watermarked  │
│                       │    + Proof     │
└───────────────────────┘                │
```

### Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Injection Speed | <1ms/vector | CPU single-threaded |
| Detection Speed | <0.5ms/vector | Correlation operation |
| Memory Overhead | 0 bytes | No extra storage needed |
| Embedding Distortion | <2% | At strength=0.5 |
| Dimension Support | 384-1536 | Tested on 768 |

---

## 🗺️ **Roadmap**

### v0.3.0 (Next Release)
- 🎯 Holographic watermarking (3-chunk redundancy)
- 📉 Improved FPR (~0.5%) and TPR (~75% @ 20% noise)
- 📦 PyPI publication
- 🔒 Enhanced security options

### v0.4.0 (Future)
- 🔐 Mandatory secret_key enforcement
- 🧪 Extended attack resistance testing
- 🌐 REST API for enterprise integration
- 📊 Dashboard for watermark management

---

## 📚 **Documentation**

- **[VALIDATION.md](./VALIDATION.md)** - Detailed test methodology and results
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
- **[docs/whitepaper.md](./docs/whitepaper.md)** - Technical deep dive

---

## 🤝 **Contributing**

We welcome contributions in:
- Statistical validation with larger datasets
- Security audits and penetration testing
- Integration with other vector databases
- Performance optimization

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📜 **License**

MIT License - See [LICENSE](./LICENSE)

Free for commercial and research use.

---

## 👤 **Credits**

Created by **Franco Luciano Carricondo** (DNI 35.664.619)

**Building digital sovereignty from Argentina.** 🇦🇷

---

## 📞 **Contact & Support**

- 🐛 GitHub Issues: [Report bugs](https://github.com/ProtocoloAEE/aee-protocol/issues)
- 📧 Email: francocarricondo@gmail.com
- 💼 LinkedIn: [Franco Carricondo](https://linkedin.com/in/francocarricondo)

---

**Last Updated:** December 15, 2024  
**Status:** Beta - Functional with documented limitations  
**Version:** 0.2.5 (Engine v8.3-Secure)