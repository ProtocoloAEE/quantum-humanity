from sqlalchemy import (
    create_engine, Column, String, DateTime, Integer, Boolean,
    JSON, Text, Index, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import NullPool
from datetime import datetime, timezone
import uuid
import logging
import os
from typing import Optional, List, Dict, Any

logger = logging.getLogger('AEE-Database')
Base = declarative_base()

class CertificateModel(Base):
    __tablename__ = 'certificates'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False, index=True)
    hash_sha256 = Column(String(64), nullable=False, unique=True, index=True)
    file_size_bytes = Column(Integer, nullable=False)
    ed25519_public = Column(String(128), nullable=False)
    kyber_public = Column(Text, nullable=False)
    signature_classic = Column(String(128), nullable=False)
    pqc_seal = Column(Text, nullable=True)
    pqc_auth_tag = Column(String(64), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp_ntp = Column(JSON, nullable=False)
    fecha_certificacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    estado = Column(String(20), default='VIGENTE', index=True)
    is_revoked = Column(Boolean, default=False, index=True)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    audit_logs = relationship('AuditLogModel', back_populates='certificate', cascade='all, delete-orphan')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'certificado_id': self.id,
            'filename': self.filename,
            'hash_sha256': self.hash_sha256,
            'fecha_certificacion': self.fecha_certificacion.isoformat() if self.fecha_certificacion else None,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AuditLogModel(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(36), ForeignKey('certificates.id'), nullable=True, index=True)
    operation = Column(String(50), nullable=False, index=True)
    action_result = Column(String(20), nullable=False)
    actor = Column(String(255), nullable=False, index=True)
    response_status = Column(Integer, nullable=False)
    tamper_detected = Column(Boolean, default=False, index=True)
    timestamp_utc = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    certificate = relationship('CertificateModel', back_populates='audit_logs')

class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///aee.db')
        self._engine = create_engine(self.database_url, connect_args={'check_same_thread': False}, poolclass=NullPool)
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    def create_all(self):
        """Crea todas las tablas en la base de datos"""
        Base.metadata.create_all(bind=self._engine)
        logger.info("[DATABASE] Tablas creadas exitosamente")

    def get_db(self):
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

db_config = DatabaseConfig()
get_db = db_config.get_db

class CertificateRepository:
    @staticmethod
    def create(db: Session, cert_dict: dict, actor: str) -> CertificateModel:
        cert = CertificateModel(
            filename=cert_dict['filename'],
            hash_sha256=cert_dict['hash_sha256'],
            file_size_bytes=cert_dict['file_size_bytes'],
            ed25519_public=cert_dict['ed25519_public'],
            kyber_public=cert_dict['kyber_public'],
            signature_classic=cert_dict['signature_classic'],
            pqc_seal=cert_dict.get('pqc_seal'),
            pqc_auth_tag=cert_dict.get('pqc_auth_tag'),
            metadata_json=cert_dict.get('metadata'),
            timestamp_ntp=cert_dict['timestamp_ntp'],
            created_by=actor
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert

    @staticmethod
    def get_by_id(db: Session, cert_id: str):
        return db.query(CertificateModel).filter(CertificateModel.id == cert_id).first()

class AuditLogRepository:
    @staticmethod
    def log(db: Session, operation: str, action_result: str, actor: str, **kwargs):
        log_entry = AuditLogModel(
            operation=operation,
            action_result=action_result,
            actor=actor,
            certificate_id=kwargs.get('certificate_id'),
            response_status=kwargs.get('response_status', 200),
            tamper_detected=kwargs.get('tamper_detected', False)
        )
        db.add(log_entry)
        db.commit()
        return log_entry