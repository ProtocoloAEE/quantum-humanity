# Archivo: src/aee/api/models.py
# ============================================================================
# PYDANTIC MODELS - Esquemas de validación para API REST
# ============================================================================

from pydantic import BaseModel, Field, FileUrl, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class MetadataInput(BaseModel):
    """Metadata opcional para certificado"""
    caso_numero: Optional[str] = Field(None, description="Número de expediente/caso")
    perito_nombre: Optional[str] = Field(None, description="Nombre del perito")
    perito_email: Optional[str] = Field(None, description="Email del perito")
    institucion: Optional[str] = Field(None, description="Institución (Fiscalía, PGN, etc)")
    notas: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "caso_numero": "2025-CV-00123",
                "perito_nombre": "Dr. Juan García",
                "institucion": "Fiscalía Federal",
                "notas": "Evidencia de delito cibernético"
            }
        }


class CertifyRequest(BaseModel):
    """Request para endpoint /certify"""
    filename: str = Field(..., description="Nombre del archivo")
    file_hash: str = Field(..., description="SHA256 del archivo en hex (64 chars)")
    file_size_bytes: int = Field(..., gt=0, description="Tamaño del archivo")
    metadata: Optional[MetadataInput] = None
    
    @validator('file_hash')
    def validate_hash(cls, v):
        if len(v) != 64:
            raise ValueError('SHA256 debe tener 64 caracteres hexadecimales')
        try:
            int(v, 16)
        except ValueError:
            raise ValueError('SHA256 debe ser válido hexadecimal')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "email_prueba.eml",
                "file_hash": "e3a5c2f1d3b8a9c7e1f5g3h2i4j6k8l0",
                "file_size_bytes": 2048,
                "metadata": {
                    "caso_numero": "2025-CV-00123",
                    "perito_nombre": "Dr. Juan García"
                }
            }
        }


class DualSignatureResponse(BaseModel):
    """Respuesta con firma dual"""
    signature_classic: str = Field(..., description="Firma Ed25519 en hex")
    pqc_seal: Optional[str] = Field(..., description="Sello Kyber-768 en hex")
    pqc_auth_tag: Optional[str] = Field(..., description="Auth tag PQC en hex")
    timestamp: str = Field(..., description="Timestamp ISO 8601 UTC")
    algorithm_classic: str = Field(default="Ed25519")
    algorithm_pqc: str = Field(default="Kyber-768")


class NTPQuorumResponse(BaseModel):
    """Respuesta del quórum NTP"""
    timestamp_unix: float
    timestamp_iso: str
    fuente: str
    servidores_consultados: int = Field(default=5)
    desviacion_ms: float


class CertificateResponse(BaseModel):
    """Response de /certify - Certificado híbrido completo"""
    certificado_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único del certificado")
    hash_sha256: str = Field(..., description="SHA256 del archivo")
    timestamp_ntp: Dict[str, Any] = Field(..., description="Quórum NTP consenso")
    archivo: Dict[str, Any] = Field(..., description="Info del archivo")
    metadata: Optional[Dict[str, Any]] = None
    claves_publicas: Dict[str, Any] = Field(..., description="Claves públicas (Ed25519 + Kyber)")
    firmas: DualSignatureResponse = Field(..., description="Firma dual")
    version_protocolo: str = Field(default="2.2.0-HybridPQC")
    fecha_certificacion: str = Field(..., description="ISO 8601 UTC")
    estado: str = Field(default="VIGENTE", description="VIGENTE, REVOCADO, EXPIRADO")
    
    class Config:
        json_schema_extra = {
            "example": {
                "certificado_id": "550e8400-e29b-41d4-a716-446655440000",
                "hash_sha256": "e3a5c2f1d3b8a9c7e1f5g3h2i4j6k8l0",
                "timestamp_ntp": {"timestamp_iso": "2025-12-30T08:41:30Z"},
                "archivo": {"nombre": "email_prueba.eml", "tamano_bytes": 2048},
                "estado": "VIGENTE"
            }
        }


class VerifyRequest(BaseModel):
    """Request para endpoint /verify"""
    file_hash: str = Field(..., description="SHA256 del archivo a verificar")
    certificado: CertificateResponse = Field(..., description="Certificado AEE completo")
    
    @validator('file_hash')
    def validate_hash(cls, v):
        if len(v) != 64:
            raise ValueError('SHA256 debe tener 64 caracteres')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_hash": "e3a5c2f1d3b8a9c7e1f5g3h2i4j6k8l0",
                "certificado": {
                    "hash_sha256": "e3a5c2f1d3b8a9c7e1f5g3h2i4j6k8l0"
                }
            }
        }


class VerificationDetail(BaseModel):
    """Detalle individual de verificación"""
    exitoso: bool
    mensaje: str
    timestamp_verificacion: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class VerifyResponse(BaseModel):
    """Response de /verify - Resultado de verificación"""
    exitoso: bool = Field(..., description="¿Certificado válido?")
    mensaje: str = Field(..., description="Mensaje descriptivo")
    verificaciones: Dict[str, Any] = Field(..., description="Detalles por componente")
    timestamp_verificacion: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    integridad: VerificationDetail = Field(..., description="Hash OK?")
    autenticidad: VerificationDetail = Field(..., description="Firma Ed25519 OK?")
    post_cuantica: Optional[VerificationDetail] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "exitoso": True,
                "mensaje": "Certificado válido (firma clásica Ed25519 verificada).",
                "integridad": {
                    "exitoso": True,
                    "mensaje": "Hash del archivo válido."
                },
                "autenticidad": {
                    "exitoso": True,
                    "mensaje": "Firma Ed25519 válida."
                },
                "post_cuantica": {
                    "exitoso": None,
                    "mensaje": "Sello PQC presente. Requiere clave privada de auditor para verificar."
                }
            }
        }


class ErrorResponse(BaseModel):
    """Respuesta de error estandarizada"""
    error: str
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "SHA256 debe tener 64 caracteres hexadecimales",
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
