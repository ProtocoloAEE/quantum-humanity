# ============================================================================
# Archivo: src/aee/api/fastapi_server.py
# APLICACIÓN FASTAPI - Configuración e integración de nivel forense
# Versión: 2.2.0-HARDENED - Security Hardening Post-Fuzz-Testing
# ============================================================================

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import logging
import sys
import traceback
from pathlib import Path
from typing import Callable

from .routes import router as api_router
from .models import ErrorResponse
from aee.infrastructure.database import db_config
from contextlib import asynccontextmanager

# Forzar codificación UTF-8 en stdout para evitar UnicodeEncodeError en Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar logging profesional con archivo forense
forensic_log_path = Path('aee_forensic.log')
forensic_handler = logging.FileHandler(forensic_log_path, encoding='utf-8')
forensic_handler.setLevel(logging.ERROR)
forensic_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n%(funcName)s\n'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        forensic_handler
    ]
)
logger = logging.getLogger('AEE-API-Server')
forensic_logger = logging.getLogger('AEE-Forensic')
forensic_logger.addHandler(forensic_handler)
forensic_logger.setLevel(logging.ERROR)

# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión de ciclo de vida del servidor - Startup y Shutdown"""
    # Startup Sequence
    logger.info("-" * 80)
    logger.info("[STARTUP] AEE Protocol v2.2.0-HARDENED - Forensic Certification Engine")
    logger.info("[STARTUP] Security Hardening: Strict Validation, Payload Limits, Global Exception Shield")
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
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARES DE SEGURIDAD (Hardening v2.2.0)
# ============================================================================

# Limitador de Payload - Protección contra DoS por saturación de memoria
class PayloadSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware que rechaza peticiones mayores a 1MB para prevenir DoS.
    v2.2.0: Verifica Content-Length antes de procesar el body.
    
    Nota: Starlette/FastAPI ya tiene límites de body, pero este middleware
    proporciona rechazo temprano basado en Content-Length para eficiencia.
    """
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB
    
    async def dispatch(self, request: StarletteRequest, call_next: Callable):
        # Verificar Content-Length si está presente (método más eficiente)
        # Esto permite rechazar peticiones grandes sin leer el body
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.MAX_PAYLOAD_SIZE:
                    client_ip = request.client.host if request.client else 'unknown'
                    logger.warning(
                        f"[SECURITY] Payload rechazado por tamaño: {size} bytes > "
                        f"{self.MAX_PAYLOAD_SIZE} bytes - Path: {request.url.path} - Client: {client_ip}"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content=ErrorResponse(
                            error="PAYLOAD_TOO_LARGE",
                            detail=f"El tamaño de la petición ({size} bytes) excede el límite máximo de {self.MAX_PAYLOAD_SIZE} bytes (1MB)"
                        ).dict()
                    )
            except ValueError:
                # Content-Length inválido, registrar pero continuar
                logger.warning(f"[SECURITY] Content-Length inválido: {content_length}")
        
        # Continuar con la petición
        # Starlette/FastAPI manejará el límite de body en la lectura real
        response = await call_next(request)
        return response

# Aplicar middlewares en orden (el más externo primero)
app.add_middleware(PayloadSizeLimitMiddleware)

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
# EXCEPTION HANDLERS - Escudo Global v2.2.0
# Garantiza que NUNCA se crashee el proceso, registra todo en aee_forensic.log
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
async def global_exception_shield(request: Request, exc: Exception):
    """
    Escudo Global de Excepciones v2.2.0
    
    Garantías de seguridad:
    - NUNCA permite que el proceso de Uvicorn se detenga
    - Registra traceback completo en aee_forensic.log
    - Devuelve HTTP 500 con mensaje genérico (sin fuga de información)
    - Captura TODAS las excepciones no controladas
    """
    # Generar ID único para rastrear el error
    error_id = f"ERR-{id(exc)}-{hash(str(exc))}"
    
    # Obtener información de la petición
    request_info = {
        'method': request.method,
        'url': str(request.url),
        'path': request.url.path,
        'client': request.client.host if request.client else 'unknown',
        'headers': dict(request.headers)
    }
    
    # Construir traceback completo
    exc_type = type(exc).__name__
    exc_message = str(exc)
    exc_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    
    # Registrar en log forense con toda la información
    forensic_logger.error(
        f"\n{'='*80}\n"
        f"UNHANDLED EXCEPTION - Error ID: {error_id}\n"
        f"Exception Type: {exc_type}\n"
        f"Exception Message: {exc_message}\n"
        f"Request Info: {request_info}\n"
        f"Full Traceback:\n{exc_traceback}\n"
        f"{'='*80}\n"
    )
    
    # También registrar en logger estándar (sin traceback completo para no saturar)
    logger.error(
        f"[RUNTIME_ERROR] ID: {error_id} - Type: {exc_type} - Message: {exc_message} - "
        f"Path: {request.url.path} - Client: {request_info['client']}"
    )
    
    # Devolver respuesta genérica (sin fuga de información)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_INFRASTRUCTURE_ERROR",
            detail="Error interno del servidor. El incidente ha sido registrado en los logs de auditoría forense."
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
        version="2.2.0",
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