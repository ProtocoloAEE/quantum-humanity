import logging
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from functools import partial

from .models import (
    CertifyRequest, CertificateResponse, VerifyRequest, VerifyResponse,
    VerificationDetail, ErrorResponse
)
from aee.pqc_hybrid import HybridCryptoEngine, DualSignature
from aee.core import RobustNTPQuorum, CanonicalJSONSerializer
from aee.infrastructure.database import (
    get_db, CertificateRepository, AuditLogRepository
)
from aee.infrastructure.security import verify_api_key

router = APIRouter(prefix="/api/v1", tags=["AEE Forensic"])
logger = logging.getLogger('AEE-API')

# Thread pool para operaciones criptográficas síncronas con timeout
crypto_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crypto-op")
CRYPTO_OPERATION_TIMEOUT = 30  # segundos - timeout para operaciones criptográficas

def get_crypto_engine(): return HybridCryptoEngine()
def get_ntp_quorum(): return RobustNTPQuorum()

@router.post("/certify", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
async def certify(
    request: CertifyRequest,
    db: Session = Depends(get_db),
    client_info: dict = Depends(verify_api_key),
    engine: HybridCryptoEngine = Depends(get_crypto_engine),
    ntp: RobustNTPQuorum = Depends(get_ntp_quorum)
):
    """
    Endpoint de certificación con timeouts y validación estricta v2.2.0
    """
    actor = client_info.get("name", "API_USER")
    
    try:
        # Validación temprana de entrada para evitar procesar basura
        if not request.file_hash or len(request.file_hash) != 64:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="file_hash debe tener exactamente 64 caracteres hexadecimales"
            )
        
        # Operaciones criptográficas con timeout para evitar bloqueos
        loop = asyncio.get_event_loop()
        
        # Generar par de claves con timeout
        try:
            keypair = await asyncio.wait_for(
                loop.run_in_executor(crypto_executor, engine.generar_par_claves_hibrido),
                timeout=CRYPTO_OPERATION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"[TIMEOUT] Generación de claves excedió {CRYPTO_OPERATION_TIMEOUT}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Operación criptográfica excedió el tiempo máximo permitido"
            )
        
        # Obtener timestamp NTP con timeout
        try:
            ntp_data = await asyncio.wait_for(
                loop.run_in_executor(crypto_executor, ntp.obtener_timestamp_consenso),
                timeout=10  # NTP más corto porque puede depender de red
            )
        except asyncio.TimeoutError:
            logger.error(f"[TIMEOUT] Quórum NTP excedió 10s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="No se pudo obtener timestamp consensuado (timeout NTP)"
            )
        except RuntimeError as e:
            # Error en quórum NTP (no timeout, sino error de consenso)
            logger.error(f"[NTP_ERROR] {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de timestamp temporal no disponible"
            )
        
        # Construir certificado base
        cert_base = {
            'hash_sha256': request.file_hash,
            'timestamp_ntp': ntp_data,
            'archivo': {'nombre': request.filename, 'tamano_bytes': request.file_size_bytes},
            'metadata': request.metadata.dict() if request.metadata else {},
            'claves_publicas': keypair.to_dict()
        }
        
        # Serialización canónica (operación rápida, sin timeout necesario)
        try:
            mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)
        except Exception as e:
            logger.error(f"[SERIALIZATION_ERROR] {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error al serializar certificado"
            )
        
        # Firma dual con timeout
        try:
            dual_sig = await asyncio.wait_for(
                loop.run_in_executor(
                    crypto_executor,
                    partial(engine.firmar_dual, mensaje_canonical, keypair)
                ),
                timeout=CRYPTO_OPERATION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"[TIMEOUT] Firma dual excedió {CRYPTO_OPERATION_TIMEOUT}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Operación de firma excedió el tiempo máximo permitido"
            )
        except (ValueError, RuntimeError) as e:
            # Errores de formato/criptográficos
            logger.error(f"[CRYPTO_ERROR] {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error en operación criptográfica: {str(e)}"
            )
        
        # Persistir certificado
        cert_data = {
            'filename': request.filename,
            'hash_sha256': request.file_hash,
            'file_size_bytes': request.file_size_bytes,
            'ed25519_public': keypair.ed25519_public.hex(),
            'kyber_public': keypair.kyber_public.hex(),
            'signature_classic': dual_sig.signature_classic.hex(),
            'pqc_seal': dual_sig.pqc_seal.hex() if dual_sig.pqc_seal else None,
            'pqc_auth_tag': dual_sig.pqc_auth_tag.hex() if dual_sig.pqc_auth_tag else None,
            'metadata': request.metadata.dict() if request.metadata else None,
            'timestamp_ntp': ntp_data
        }
        
        try:
            cert_model = CertificateRepository.create(db, cert_data, actor)
            AuditLogRepository.log(db, "CERTIFY", "SUCCESS", actor, certificate_id=cert_model.id, response_status=201)
        except Exception as e:
            logger.error(f"[DB_ERROR] Error al persistir certificado: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al persistir certificado en base de datos"
            )

        return CertificateResponse(
            certificado_id=cert_model.id,
            hash_sha256=request.file_hash,
            timestamp_ntp=ntp_data,
            archivo=cert_base['archivo'],
            metadata=cert_base['metadata'],
            claves_publicas=cert_base['claves_publicas'],
            firmas={
                'signature_classic': dual_sig.signature_classic.hex(),
                'pqc_seal': dual_sig.pqc_seal.hex() if dual_sig.pqc_seal else None,
                'pqc_auth_tag': dual_sig.pqc_auth_tag.hex() if dual_sig.pqc_auth_tag else None,
                'timestamp': dual_sig.timestamp
            },
            fecha_certificacion=datetime.now(timezone.utc).isoformat(),
            estado="VIGENTE"
        )
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        # Cualquier otro error no controlado
        logger.error(f"[UNEXPECTED_ERROR] Certify: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la certificación"
        )

@router.post("/verify", response_model=VerifyResponse)
async def verify(
    request: VerifyRequest,
    db: Session = Depends(get_db),
    client_info: dict = Depends(verify_api_key),
    engine: HybridCryptoEngine = Depends(get_crypto_engine)
):
    """
    Endpoint de verificación con timeouts y validación estricta v2.2.0
    """
    actor = client_info.get("name", "API_USER")
    
    try:
        # Validación temprana de entrada
        if not request.file_hash or len(request.file_hash) != 64:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="file_hash debe tener exactamente 64 caracteres hexadecimales"
            )
        
        # Verificar hash
        hash_match = request.file_hash.lower() == request.certificado.hash_sha256.lower()
        
        # Construir certificado base para serialización
        try:
            cert_base = {
                'hash_sha256': request.certificado.hash_sha256,
                'timestamp_ntp': request.certificado.timestamp_ntp,
                'archivo': request.certificado.archivo,
                'metadata': request.certificado.metadata,
                'claves_publicas': request.certificado.claves_publicas
            }
            mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)
        except Exception as e:
            logger.error(f"[SERIALIZATION_ERROR] Verify: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error al serializar certificado para verificación"
            )
        
        # Construir DualSignature con validación de formato
        try:
            f = request.certificado.firmas
            if not f.get('signature_classic'):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Certificado no contiene signature_classic"
                )
            
            # Validar formato hex antes de convertir
            try:
                sig_bytes = bytes.fromhex(f['signature_classic'])
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"signature_classic no es hexadecimal válido: {str(e)}"
                )
            
            dual_sig = DualSignature(
                signature_classic=sig_bytes,
                pqc_seal=bytes.fromhex(f['pqc_seal']) if f.get('pqc_seal') else None,
                pqc_auth_tag=bytes.fromhex(f['pqc_auth_tag']) if f.get('pqc_auth_tag') else None,
                timestamp=f['timestamp']
            )
            
            # Validar y convertir clave pública
            try:
                pub_key_hex = request.certificado.claves_publicas.get('ed25519_public')
                if not pub_key_hex:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Certificado no contiene ed25519_public"
                    )
                pub_key_ed = bytes.fromhex(pub_key_hex)
                if len(pub_key_ed) != 32:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="ed25519_public debe ser exactamente 32 bytes (64 chars hex)"
                    )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"ed25519_public no es hexadecimal válido: {str(e)}"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[FORMAT_ERROR] Verify: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error al procesar formato del certificado: {str(e)}"
            )
        
        # Verificar firma con timeout
        loop = asyncio.get_event_loop()
        try:
            firma_ok, detalle = await asyncio.wait_for(
                loop.run_in_executor(
                    crypto_executor,
                    partial(engine.verificar_dual, mensaje_canonical, dual_sig, pub_key_ed)
                ),
                timeout=CRYPTO_OPERATION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"[TIMEOUT] Verificación de firma excedió {CRYPTO_OPERATION_TIMEOUT}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Operación de verificación excedió el tiempo máximo permitido"
            )
        except (ValueError, RuntimeError) as e:
            # Errores de formato/criptográficos
            logger.error(f"[CRYPTO_ERROR] Verify: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error en verificación criptográfica: {str(e)}"
            )
        
        exitoso = hash_match and firma_ok
        
        # Registrar en auditoría
        try:
            AuditLogRepository.log(
                db, "VERIFY", "SUCCESS" if exitoso else "TAMPER_DETECTED", actor, 
                certificate_id=request.certificado.certificado_id, tamper_detected=not exitoso
            )
        except Exception as e:
            logger.warning(f"[AUDIT_LOG_ERROR] No se pudo registrar en auditoría: {str(e)}")
            # No fallar la verificación si falla el log de auditoría

        return VerifyResponse(
            exitoso=exitoso,
            mensaje="Certificado válido" if exitoso else "Fallo de integridad o autenticidad",
            integridad=VerificationDetail(
                exitoso=hash_match, 
                mensaje="Hash del archivo coincide con el certificado" if hash_match else "Hash del archivo no coincide"
            ),
            autenticidad=VerificationDetail(
                exitoso=firma_ok, 
                mensaje=detalle.get('mensaje_ed25519', 'Verificación completada')
            ),
            verificaciones=detalle
        )
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        # Cualquier otro error no controlado
        logger.error(f"[UNEXPECTED_ERROR] Verify: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la verificación"
        )

@router.get("/health")
async def health(): 
    return {"status": "OK", "version": "2.3.0"}