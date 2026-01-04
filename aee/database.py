"""
aee/database.py
Módulo de persistencia de datos usando SQLAlchemy y SQLite.
Gestiona almacenamiento de preservaciones digitales con integridad.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os

logger = logging.getLogger(__name__)

# Configuración de base de datos
DATABASE_PATH = os.getenv("DATABASE_PATH", "aee_preservations.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Crear base para los modelos
Base = declarative_base()

# ============================================================================
# MODELO DE TABLA: Preservations
# ============================================================================

class PreservationRecord(Base):
    """
    Modelo de registro de preservación digital.
    
    Campos:
        id: Identificador único del registro
        file_hash: Hash SHA-256 del archivo (64 caracteres hexadecimales)
        file_name: Nombre original del archivo (ej: documento.pdf)
        mime_type: Tipo MIME del archivo (ej: image/jpeg)
        file_size: Tamaño del archivo en bytes
        user_id: ID del usuario de Telegram que subió el archivo
        timestamp_utc: Marca de tiempo UTC de la preservación (RFC 3339)
        pqc_signature: Campo reservado para firma post-cuántica (Dilithium/Kyber)
    """
    __tablename__ = 'preservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(String(20), nullable=False, index=True)
    timestamp_utc = Column(DateTime, nullable=False, default=datetime.utcnow)
    pqc_signature = Column(Text, nullable=True)  # Para Dilithium/Kyber futuro
    
    def __repr__(self):
        return (
            f"<PreservationRecord("
            f"id={self.id}, "
            f"hash={self.file_hash[:16]}..., "
            f"size={self.file_size}, "
            f"timestamp={self.timestamp_utc}"
            f")>"
        )
    
    def to_dict(self) -> dict:
        """Convierte el registro a diccionario para serialización."""
        return {
            'id': self.id,
            'file_hash': self.file_hash,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'timestamp_utc': self.timestamp_utc.isoformat() + 'Z',
            'pqc_signature': self.pqc_signature
        }


# ============================================================================
# GESTOR DE BASE DE DATOS
# ============================================================================

class DatabaseManager:
    """
    Gestor centralizado de operaciones de base de datos.
    Proporciona métodos CRUD para preservaciones digitales.
    """
    
    _engine = None
    _SessionLocal = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """
        Inicializa la base de datos y crea las tablas si no existen.
        Debe llamarse una sola vez al inicio de la aplicación.
        """
        try:
            logger.info(f"Inicializando base de datos: {DATABASE_URL}")
            
            # Crear engine
            cls._engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},  # SQLite requiere esto para threading
                echo=False  # Cambiar a True para ver SQL queries
            )
            
            # Crear sesion factory
            cls._SessionLocal = sessionmaker(
                bind=cls._engine,
                autocommit=False,
                autoflush=False
            )
            
            # Crear todas las tablas
            Base.metadata.create_all(bind=cls._engine)
            
            cls._initialized = True
            logger.info("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.exception(f"❌ Error al inicializar base de datos: {type(e).__name__}: {e}")
            raise
    
    @classmethod
    def get_session(cls) -> Session:
        """
        Obtiene una sesión de base de datos.
        Debe usarse con context manager o llamar a close() manualmente.
        """
        if not cls._initialized:
            cls.initialize()
        
        return cls._SessionLocal()
    
    @classmethod
    def add_preservation(cls, file_hash: str, file_name: str, mime_type: str,
                        file_size: int, user_id: str) -> PreservationRecord:
        """
        Registra una preservación digital en la base de datos.
        
        Args:
            file_hash: Hash SHA-256 del archivo (64 caracteres)
            file_name: Nombre del archivo
            mime_type: Tipo MIME
            file_size: Tamaño en bytes
            user_id: ID del usuario (Telegram)
        
        Returns:
            PreservationRecord: El registro creado
        
        Raises:
            ValueError: Si el hash ya existe
            SQLAlchemyError: Si hay error en la BD
        """
        session = None
        try:
            session = cls.get_session()
            
            # Validar que el hash sea válido (64 caracteres hexadecimales)
            if not isinstance(file_hash, str) or len(file_hash) != 64:
                raise ValueError(f"Hash inválido: debe ser 64 caracteres hex, recibido: {file_hash}")
            
            # Verificar si el hash ya existe
            existing = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            if existing:
                logger.warning(f"Hash duplicado detectado: {file_hash}")
                raise ValueError(f"El archivo ya ha sido preservado: {file_hash}")
            
            # Crear nuevo registro
            preservation = PreservationRecord(
                file_hash=file_hash,
                file_name=file_name,
                mime_type=mime_type,
                file_size=file_size,
                user_id=user_id,
                timestamp_utc=datetime.utcnow()
            )
            
            session.add(preservation)
            session.commit()
            
            logger.info(
                f"✅ Preservación registrada: ID={preservation.id}, "
                f"Hash={file_hash[:16]}..., User={user_id}"
            )
            
            return preservation
            
        except ValueError as e:
            logger.warning(f"Validación fallida: {e}")
            if session:
                session.rollback()
            raise
            
        except SQLAlchemyError as e:
            logger.exception(f"Error de base de datos: {type(e).__name__}: {e}")
            if session:
                session.rollback()
            raise
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def get_preservation_by_hash(cls, file_hash: str) -> PreservationRecord:
        """
        Busca un registro de preservación por su hash SHA-256.
        
        Args:
            file_hash: Hash SHA-256
        
        Returns:
            PreservationRecord o None si no existe
        """
        session = None
        try:
            session = cls.get_session()
            record = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            
            if record:
                logger.debug(f"Preservación encontrada: ID={record.id}")
            else:
                logger.debug(f"Preservación no encontrada: {file_hash}")
            
            return record
            
        except Exception as e:
            logger.exception(f"Error en get_preservation_by_hash: {type(e).__name__}: {e}")
            return None
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def get_preservations_by_user(cls, user_id: str) -> list:
        """
        Lista todas las preservaciones de un usuario.
        
        Args:
            user_id: ID del usuario (Telegram)
        
        Returns:
            Lista de PreservationRecord
        """
        session = None
        try:
            session = cls.get_session()
            records = session.query(PreservationRecord).filter_by(user_id=user_id).all()
            
            logger.debug(f"Se encontraron {len(records)} preservaciones para usuario {user_id}")
            
            return records
            
        except Exception as e:
            logger.exception(f"Error en get_preservations_by_user: {type(e).__name__}: {e}")
            return []
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def get_preservation_by_id(cls, preservation_id: int) -> PreservationRecord:
        """
        Obtiene un registro por su ID.
        
        Args:
            preservation_id: ID del registro
        
        Returns:
            PreservationRecord o None
        """
        session = None
        try:
            session = cls.get_session()
            record = session.query(PreservationRecord).filter_by(id=preservation_id).first()
            
            return record
            
        except Exception as e:
            logger.exception(f"Error en get_preservation_by_id: {type(e).__name__}: {e}")
            return None
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def update_pqc_signature(cls, file_hash: str, signature: str) -> bool:
        """
        Actualiza la firma post-cuántica de un registro.
        (Para uso futuro con Dilithium/Kyber)
        
        Args:
            file_hash: Hash SHA-256
            signature: Firma PQC en hexadecimal
        
        Returns:
            True si se actualizó, False si no encontró el registro
        """
        session = None
        try:
            session = cls.get_session()
            
            record = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            
            if not record:
                logger.warning(f"Registro no encontrado para actualizar: {file_hash}")
                return False
            
            record.pqc_signature = signature
            session.commit()
            
            logger.info(f"✅ Firma PQC actualizada: {file_hash[:16]}...")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error en update_pqc_signature: {type(e).__name__}: {e}")
            if session:
                session.rollback()
            return False
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def get_all_preservations(cls, limit: int = 100) -> list:
        """
        Obtiene los últimos N registros de preservación.
        
        Args:
            limit: Número máximo de registros a retornar
        
        Returns:
            Lista de PreservationRecord ordenados por timestamp descendente
        """
        session = None
        try:
            session = cls.get_session()
            
            records = session.query(PreservationRecord)\
                .order_by(PreservationRecord.timestamp_utc.desc())\
                .limit(limit)\
                .all()
            
            logger.debug(f"Se obtuvieron {len(records)} registros (limit={limit})")
            
            return records
            
        except Exception as e:
            logger.exception(f"Error en get_all_preservations: {type(e).__name__}: {e}")
            return []
            
        finally:
            if session:
                session.close()
    
    @classmethod
    def delete_preservation(cls, file_hash: str) -> bool:
        """
        Elimina un registro de preservación (uso administrativo).
        
        Args:
            file_hash: Hash SHA-256
        
        Returns:
            True si se eliminó, False si no existía
        """
        session = None
        try:
            session = cls.get_session()
            
            record = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            
            if not record:
                logger.warning(f"Registro no encontrado para eliminar: {file_hash}")
                return False
            
            session.delete(record)
            session.commit()
            
            logger.info(f"✅ Registro eliminado: {file_hash[:16]}...")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error en delete_preservation: {type(e).__name__}: {e}")
            if session:
                session.rollback()
            return False
            
        finally:
            if session:
                session.close()


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def init_database():
    """
    Función de inicialización para llamar desde main.py
    """
    DatabaseManager.initialize()
