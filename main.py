from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from aee_v8 import AEEv8, LegalCertification, AEEv8Legal  # Ajusta import

# Modelos Pydantic
class EmbeddingRequest(BaseModel):
    embedding: List[float]
    metadata: Optional[Dict] = None
    operation: str = "inject" # "inject" o "detect"

class BatchRequest(BaseModel):
    embeddings: List[List[float]]
    operation: str = "detect"

class PineconeUpsertRequest(BaseModel):
    vectors: List[Tuple[str, List[float], Dict]]
    namespace: str = ""

class LegalInjectionRequest(BaseModel):
    embedding: List[float]
    content_info: Optional[Dict] = None

# Inicializar FastAPI
app = FastAPI(
    title="AEE v8 API",
    description="API de trazabilidad vectorial con certificación legal",
    version="8.0.0"
)

security = HTTPBearer()

# Sistema AEE global (en producción usaría inyección de dependencias)
aee_system = None
legal_system = None

def get_aee_system():
    """Obtener sistema AEE (singleton)."""
    global aee_system
    if aee_system is None:
        aee_system = AEEv8(user_id=35664619)
    return aee_system

def get_legal_system():
    """Obtener sistema legal (singleton)."""
    global legal_system
    if legal_system is None:
        legal_system = LegalCertification()
    return legal_system

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar."""
    print("🚀 AEE v8 API iniciando...")
   
    global aee_system, legal_system
    aee_system = AEEv8(user_id=35664619, auto_calibrate=True)
    legal_system = LegalCertification()
   
    print(f"✅ Sistema AEE v{aee_system.VERSION} inicializado")
    print(f" User ID: {aee_system.user_id}")

@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "service": "AEE v8 - Vector Traceability",
        "version": "8.0.0",
        "status": "operational",
        "endpoints": {
            "/inject": "Inyectar marca en embedding",
            "/detect": "Detectar marca en embedding",
            "/batch": "Procesamiento por lotes",
            "/legal/inject": "Inyección con certificación legal",
            "/legal/verify": "Verificación con certificación legal",
            "/pinecone/upsert": "Upsert a Pinecone con marca",
            "/pinecone/query": "Query y verificación Pinecone",
            "/health": "Health check",
            "/metrics": "Métricas del sistema"
        }
    }

@app.post("/inject")
async def inject_embedding(
    request: EmbeddingRequest,
    aee: AEEv8 = Depends(get_aee_system)
):
    """Inyectar marca en embedding."""
    try:
        embedding = np.array(request.embedding)
        watermarked, metadata = aee.inject(
            embedding,
            metadata=request.metadata
        )
       
        return {
            "success": True,
            "watermarked_embedding": watermarked.tolist(),
            "metadata": metadata,
            "dimension": len(watermarked)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect")
async def detect_embedding(
    request: EmbeddingRequest,
    aee: AEEv8 = Depends(get_aee_system)
):
    """Detectar marca en embedding."""
    try:
        embedding = np.array(request.embedding)
        detection = aee.detect(embedding)
       
        return {
            "success": True,
            "detection": detection,
            "embedding_dimension": len(embedding)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch")
async def batch_process(
    request: BatchRequest,
    aee: AEEv8 = Depends(get_aee_system)
):
    """Procesamiento por lotes."""
    try:
        embeddings = [np.array(emb) for emb in request.embeddings]
        results = aee.batch_process(embeddings, operation=request.operation)
       
        return {
            "success": True,
            "operation": request.operation,
            "processed_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal/inject")
async def legal_inject(
    request: LegalInjectionRequest,
    aee: AEEv8 = Depends(get_aee_system),
    legal: LegalCertification = Depends(get_legal_system)
):
    """Inyección con certificación legal."""
    try:
        # Crear sistema legal combinado
        aee_legal = AEEv8Legal(
            user_id=aee.user_id,
            legal_certifier=legal
        )
       
        embedding = np.array(request.embedding)
        watermarked, full_metadata = aee_legal.inject_with_legal_proof(
            embedding,
            request.content_info
        )
       
        return {
            "success": True,
            "watermarked_embedding": watermarked.tolist(),
            "metadata": full_metadata,
            "certificate_id": full_metadata['legal_proof'].get('proof_id'),
            "legal_grade": "certified"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(aee: AEEv8 = Depends(get_aee_system)):
    """Health check del sistema."""
    return {
        "status": "healthy",
        "version": aee.VERSION,
        "user_id": aee.user_id,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.get("/metrics")
async def get_metrics(aee: AEEv8 = Depends(get_aee_system)):
    """Métricas del sistema."""
    return {
        "cache_size": len(aee.direction_cache),
        "cache_hits": len(aee.cache_keys),
        "threshold": aee.threshold,
        "strength": aee.strength,
        "version": aee.VERSION
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)