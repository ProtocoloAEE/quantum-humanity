# ============================================================================
# Archivo: src/aee/api/fastapi_server.py
# APLICACIÓN FASTAPI - Configuración e integración de nivel forense
# Versión: 2.1.0-HARDENED
# ============================================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import sys

from .routes import router as api_router
from .models import ErrorResponse
from aee.infrastructure.database import db_config
from contextlib import asynccontextmanager

# Forzar codificación UTF-8 en stdout para evitar UnicodeEncodeError en Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar logging profesional (Sin emojis para compatibilidad universal)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AEE-API-Server')

# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión de ciclo de vida del servidor - Startup y Shutdown"""
    # Startup Sequence
    logger.info("-" * 80)
    logger.info("[STARTUP] AEE Protocol v2.1.0-HARDENED - Forensic Certification Engine")
    logger.info("[STARTUP] Initializing Infrastructure Components...")
    
    try:
        # Inicialización de persistencia
        db_config.create_all()
        logger.info("[DATABASE] Persistence layer initialized successfully")
    except Exception as e:
        logger.critical(f"[DATABASE] Critical failure during initialization: {str(e)}")
        raise

    logger.info("[STARTUP] Server ready for incoming forensic requests")
    logger.info("-" * 80)
    
    yield
    
    # Shutdown Sequence
    logger.info("[SHUTDOWN] Terminating AEE Protocol Server...")
    logger.info("[SHUTDOWN] Closing active infrastructure connections")


# ============================================================================
# CREAR APLICACIÓN
# ============================================================================

app = FastAPI(
    title="AEE Protocol API",
    description="Motor de Certificación de Evidencia Digital con Seguridad Híbrida (Ed25519 + Kyber-768)",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARES DE SEGURIDAD (Hardening)
# ============================================================================

# CORS - Configuración restrictiva para producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.aee-protocol.io"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted Hosts - Protección contra HTTP Host Header Attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.aee-protocol.io"]
)


# ============================================================================
# EXCEPTION HANDLERS - Seguridad por Oscuridad
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Manejo de errores de validación de dominio"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="DOMAIN_VALIDATION_ERROR",
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo de excepciones no controladas - Evita fuga de stacktrace"""
    logger.error(f"[RUNTIME_ERROR] ID: {id(exc)} - Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_INFRASTRUCTURE_ERROR",
            detail="Error interno del servidor. Identificador de rastro enviado a logs de auditoría."
        ).dict()
    )


# ============================================================================
# INCLUIR ROUTERS
# ============================================================================

app.include_router(api_router)


# ============================================================================
# CUSTOM OPENAPI SCHEMA (Documentación Profesional)
# ============================================================================

def custom_openapi():
    """Generación de esquema OpenAPI conforme a estándares técnicos"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AEE Protocol - Technical Specification",
        version="2.1.0",
        description="""
### Especificación Técnica del Protocolo AEE

Sistema de aseguramiento de integridad de activos digitales basado en:
- **Criptografía Post-Cuántica:** Implementación híbrida ML-KEM (Kyber-768).
- **Firma Clásica de Alta Curva:** Ed25519 para no-repudio.
- **Protocolo de Tiempo Distribuido:** Consenso mediante quórum NTP.
- **Persistencia Forense:** Auditoría inmutable de eventos de certificación.

---
*Para guías de implementación judicial, consulte el manual de peritaje en el repositorio oficial.*
        """,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuración de ejecución segura
    uvicorn.run(
        "aee.api.fastapi_server:app",
        host="127.0.0.1", # Local por defecto para auditoría
        port=8000,
        workers=1,        # 1 worker para facilitar debugging en fase de auditoría
        log_level="info",
        reload=False
    )