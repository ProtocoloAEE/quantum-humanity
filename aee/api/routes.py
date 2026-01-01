import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from .models import (
    CertifyRequest, CertificateResponse, VerifyRequest, VerifyResponse,
    VerificationDetail
)
from aee.pqc_hybrid import HybridCryptoEngine, DualSignature
from aee.core import RobustNTPQuorum, CanonicalJSONSerializer
from aee.infrastructure.database import (
    get_db, CertificateRepository, AuditLogRepository
)
from aee.infrastructure.security import verify_api_key

router = APIRouter(prefix="/api/v1", tags=["AEE Forensic"])
logger = logging.getLogger('AEE-API')

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
    actor = client_info.get("name", "API_USER")
    try:
        # Modelo de Seguridad v2.1: No se permite degradación silenciosa
        # Todas las operaciones críticas deben completarse o lanzar excepción
        keypair = engine.generar_par_claves_hibrido()
        ntp_data = ntp.obtener_timestamp_consenso()
        cert_base = {
            'hash_sha256': request.file_hash,
            'timestamp_ntp': ntp_data,
            'archivo': {'nombre': request.filename, 'tamano_bytes': request.file_size_bytes},
            'metadata': request.metadata.dict() if request.metadata else {},
            'claves_publicas': keypair.to_dict()
        }
        mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)
        # firmar_dual lanza excepción si falla (no degradación silenciosa)
        dual_sig = engine.firmar_dual(mensaje_canonical, keypair)
        
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
        cert_model = CertificateRepository.create(db, cert_data, actor)
        AuditLogRepository.log(db, "CERTIFY", "SUCCESS", actor, certificate_id=cert_model.id, response_status=201)

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
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", response_model=VerifyResponse)
async def verify(
    request: VerifyRequest,
    db: Session = Depends(get_db),
    client_info: dict = Depends(verify_api_key),
    engine: HybridCryptoEngine = Depends(get_crypto_engine)
):
    actor = client_info.get("name", "API_USER")
    
    # Modelo de Seguridad v2.1: Verificación estricta sin degradación silenciosa
    try:
        hash_match = request.file_hash.lower() == request.certificado.hash_sha256.lower()
        
        cert_base = {
            'hash_sha256': request.certificado.hash_sha256,
            'timestamp_ntp': request.certificado.timestamp_ntp,
            'archivo': request.certificado.archivo,
            'metadata': request.certificado.metadata,
            'claves_publicas': request.certificado.claves_publicas
        }
        mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)
        f = request.certificado.firmas
        dual_sig = DualSignature(
            signature_classic=bytes.fromhex(f['signature_classic']),
            pqc_seal=bytes.fromhex(f['pqc_seal']) if f.get('pqc_seal') else None,
            pqc_auth_tag=bytes.fromhex(f['pqc_auth_tag']) if f.get('pqc_auth_tag') else None,
            timestamp=f['timestamp']
        )
        pub_key_ed = bytes.fromhex(request.certificado.claves_publicas['ed25519_public'])
        # verificar_dual lanza excepción si hay error crítico (no InvalidSignature)
        firma_ok, detalle = engine.verificar_dual(mensaje_canonical, dual_sig, pub_key_ed)
        exitoso = hash_match and firma_ok
    except (ValueError, RuntimeError) as e:
        # Errores de formato/criptográficos se propagan (no se ocultan)
        logger.error(f"Error crítico en verificación: {e}")
        raise HTTPException(status_code=422, detail=f"Error en verificación: {str(e)}")

    AuditLogRepository.log(db, "VERIFY", "SUCCESS" if exitoso else "TAMPER_DETECTED", actor, 
                           certificate_id=request.certificado.certificado_id, tamper_detected=not exitoso)

    return VerifyResponse(
        exitoso=exitoso,
        mensaje="Verificado" if exitoso else "Fallo de integridad",
        integridad=VerificationDetail(exitoso=hash_match, mensaje="Hash OK" if hash_match else "Hash mal"),
        autenticidad=VerificationDetail(exitoso=firma_ok, mensaje=detalle['mensaje_ed25519']),
        verificaciones=detalle
    )

@router.get("/health")
async def health(): return {"status": "OK", "version": "2.1.0"}