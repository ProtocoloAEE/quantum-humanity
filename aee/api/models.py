# Archivo: src/aee/api/models.py
# ============================================================================
# PYDANTIC MODELS - Esquemas de validación para API REST
# Versión: 2.2.0 - Validación estricta con regex y límites de tamaño
# ============================================================================

from pydantic import BaseModel, Field, FileUrl, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import re
import json

class MetadataInput(BaseModel):
    """Metadata opcional para certificado con límites de tamaño estrictos"""
    caso_numero: Optional[str] = Field(None, max_length=100, description="Número de expediente/caso")
    perito_nombre: Optional[str] = Field(None, max_length=200, description="Nombre del perito")
    perito_email: Optional[str] = Field(None, max_length=255, description="Email del perito")
    institucion: Optional[str] = Field(None, max_length=200, description="Institución (Fiscalía, PGN, etc)")
    notas: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    @validator('*', pre=True)
    def validate_metadata_size(cls, v):
        """Valida que el tamaño total de metadatos no supere 10KB"""
        if v is None:
            return v
        # Calcular tamaño aproximado en bytes
        if isinstance(v, str):
            size_bytes = len(v.encode('utf-8'))
            if size_bytes > 10000:  # 10KB límite por campo
                raise ValueError(f'Campo de metadata excede 10KB: {size_bytes} bytes')
        return v
    
    def model_dump_json(self, **kwargs) -> str:
        """Serializa y valida tamaño total de metadatos"""
        data = self.dict(exclude_none=True)
        json_str = json.dumps(data, ensure_ascii=False)
        total_size = len(json_str.encode('utf-8'))
        if total_size > 10240:  # 10KB límite total
            raise ValueError(f'Metadata total excede 10KB: {total_size} bytes')
        return json_str
    
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
    """Request para endpoint /certify con validación estricta v2.2.0"""
    filename: str = Field(..., max_length=500, description="Nombre del archivo (máx 500 chars)")
    file_hash: str = Field(..., description="SHA256 del archivo en hex (64 chars)")
    file_size_bytes: int = Field(..., gt=0, le=10**12, description="Tamaño del archivo (máx 1TB)")
    metadata: Optional[MetadataInput] = None
    
    @validator('file_hash')
    def validate_hash_strict(cls, v):
        """Validación estricta de hash SHA256 con regex"""
        if not isinstance(v, str):
            raise ValueError('file_hash debe ser una cadena')
        v = v.strip().lower()
        if len(v) != 64:
            raise ValueError('SHA256 debe tener exactamente 64 caracteres hexadecimales')
        if not re.match(r'^[0-9a-f]{64}$', v):
            raise ValueError('SHA256 debe contener solo caracteres hexadecimales (0-9, a-f)')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        """Valida que el filename no contenga caracteres peligrosos"""
        if not isinstance(v, str):
            raise ValueError('filename debe ser una cadena')
        # Rechazar path traversal y caracteres peligrosos
        dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', '|', ':', '*', '?']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'filename contiene caracteres peligrosos: {char}')
        if len(v.encode('utf-8')) > 500:
            raise ValueError('filename excede 500 bytes')
        return v
    
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
    hash_sha256: str = Field(..., description="SHA256 del archivo (64 chars hex)")
    timestamp_ntp: Dict[str, Any] = Field(..., description="Quórum NTP consenso")
    archivo: Dict[str, Any] = Field(..., description="Info del archivo")
    metadata: Optional[Dict[str, Any]] = None
    claves_publicas: Dict[str, Any] = Field(..., description="Claves públicas (Ed25519 + Kyber)")
    firmas: DualSignatureResponse = Field(..., description="Firma dual")
    version_protocolo: str = Field(default="2.2.0-HybridPQC")
    fecha_certificacion: str = Field(..., description="ISO 8601 UTC")
    estado: str = Field(default="VIGENTE", description="VIGENTE, REVOCADO, EXPIRADO")
    
    @validator('hash_sha256')
    def validate_hash_strict(cls, v):
        """Validación estricta de hash SHA256"""
        if not isinstance(v, str):
            raise ValueError('hash_sha256 debe ser una cadena')
        v = v.strip().lower()
        if len(v) != 64:
            raise ValueError('SHA256 debe tener exactamente 64 caracteres hexadecimales')
        if not re.match(r'^[0-9a-f]{64}$', v):
            raise ValueError('SHA256 debe contener solo caracteres hexadecimales (0-9, a-f)')
        return v
    
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
    """Request para endpoint /verify con validación estricta v2.2.0"""
    file_hash: str = Field(..., description="SHA256 del archivo a verificar (64 chars hex)")
    certificado: CertificateResponse = Field(..., description="Certificado AEE completo")
    
    @validator('file_hash')
    def validate_hash_strict(cls, v):
        """Validación estricta de hash SHA256 con regex"""
        if not isinstance(v, str):
            raise ValueError('file_hash debe ser una cadena')
        v = v.strip().lower()
        if len(v) != 64:
            raise ValueError('SHA256 debe tener exactamente 64 caracteres hexadecimales')
        if not re.match(r'^[0-9a-f]{64}$', v):
            raise ValueError('SHA256 debe contener solo caracteres hexadecimales (0-9, a-f)')
        return v
    
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
