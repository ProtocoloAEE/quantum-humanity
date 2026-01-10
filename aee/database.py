import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os
import hashlib
import json

logger = logging.getLogger(__name__)

# Configuración de base de datos
DATABASE_PATH = os.getenv("DATABASE_PATH", "aee_preservations.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Crear base para los modelos
Base = declarative_base()

# ============================================================================
# FUNCIONES DE HASHING
# ============================================================================

def calculate_file_hash(file_content: bytes, timestamp: datetime, user_id: str, device_id: str = None) -> str:
    """
    Calcula hash SHA-256 determinista de archivo + metadata crítica.
    
    Args:
        file_content: Contenido del archivo en bytes
        timestamp: Timestamp de preservación
        user_id: ID del autor
        device_id: ID del dispositivo (opcional)
    
    Returns:
        Hash SHA-256 hexadecimal (64 caracteres)
    """
    # Serializar metadata de forma determinista y normalizada
    metadata = {
        "timestamp": timestamp.isoformat() + 'Z',
        "user_id": user_id,
        "device_id": device_id or ""
    }
    metadata_json = json.dumps(metadata, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    metadata_bytes = metadata_json.encode('utf-8')
    
    # Concatenación binaria con delimitador nulo para prevenir colisiones
    combined = metadata_bytes + b'\x00' + file_content
    
    # Calcular hash
    return hashlib.sha256(combined).hexdigest()

# ============================================================================
# MODELO DE TABLA: Preservations
# ============================================================================

class PreservationRecord(Base):
    __tablename__ = 'preservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(String(20), nullable=False, index=True)
    timestamp_utc = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    device_id = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<PreservationRecord(id={self.id}, hash={self.file_hash[:16]}..., size={self.file_size})>"
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'file_hash': self.file_hash,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'timestamp_utc': self.timestamp_utc.isoformat() + 'Z',
            'device_id': self.device_id
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
            logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.exception(f"Error al inicializar base de datos: {type(e).__name__}: {e}")
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
    def add_preservation(cls, file_content: bytes, file_name: str, mime_type: str,
                        user_id: str, device_id: str = None) -> PreservationRecord:
        """
        Registra una preservación digital calculando hash de contenido + metadata.
        
        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            mime_type: Tipo MIME
            user_id: ID del usuario
            device_id: ID del dispositivo (opcional)
        
        Returns:
            PreservationRecord creado
        
        Raises:
            ValueError: Si el hash ya existe
        """
        session = None
        try:
            session = cls.get_session()
            
            # Calcular timestamp
            timestamp = datetime.now(timezone.utc)
            
            # Calcular hash determinista
            file_hash = calculate_file_hash(file_content, timestamp, user_id, device_id)
            
            # Verificar duplicado
            existing = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            if existing:
                raise ValueError(f"Archivo ya preservado: {file_hash}")
            
            # Crear registro
            preservation = PreservationRecord(
                file_hash=file_hash,
                file_name=file_name,
                mime_type=mime_type,
                file_size=len(file_content),
                user_id=user_id,
                timestamp_utc=timestamp,
                device_id=device_id
            )
            
            session.add(preservation)
            session.commit()
            
            logger.info(f"Preservación registrada: ID={preservation.id}, Hash={file_hash[:16]}...")
            
            return preservation
            
        except ValueError:
            if session:
                session.rollback()
            raise
            
        except SQLAlchemyError as e:
            logger.exception(f"Error BD: {e}")
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
    def update_cryptographic_signature(cls, file_hash: str, signature: str) -> bool:
        """
        Actualiza la firma criptográfica de un registro.
        (Para uso futuro con algoritmos criptográficos avanzados)
        
        Args:
            file_hash: Hash SHA-256
            signature: Firma criptográfica en hexadecimal
        
        Returns:
            True si se actualizó, False si no encontró el registro
        """
        session = None
        try:
            session = cls.get_session()
            
            record = session.query(PreservationRecord).filter_by(file_hash=file_hash).first()
            
            if not record:
                logger.warning(f"Registro no encontrado para actualizar: {file_hash}")
                session.rollback()
                return False
            
            record.cryptographic_signature = signature
            
            logger.info(f"Firma criptográfica actualizada: {file_hash[:16]}...")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error en update_cryptographic_signature: {type(e).__name__}: {e}")
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
            
            logger.info(f"Registro eliminado: {file_hash[:16]}...")
            
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
