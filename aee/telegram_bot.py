#!/usr/bin/env python3
"""
AEE Protocol - Telegram Bot de Certificación
Bot para certificar chats y evidencia digital mediante Protocolo AEE
"""

import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io

from aee.pqc_hybrid import HybridCryptoEngine, DualSignature
from aee.core import CanonicalJSONSerializer
from aee.infrastructure.database import get_db, CertificateRepository, AuditLogRepository

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('AEE-Telegram-Bot')

# Token del bot (configurado para @CertificadorOficialBot)
# Puede venir de variable de entorno o configurarse directamente
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8551824212:AAG2ese5vIVrxUjrV7Uv4fPVEAAPa6Y6BQs')

# Motor criptográfico global
crypto_engine = HybridCryptoEngine()


def calculate_file_hash(file_bytes: bytes) -> str:
    """Calcula SHA-256 de un archivo"""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start con mensaje profesional"""
    welcome_message = """🛡️ *Bienvenido al Certificador Oficial AEE*

Tu evidencia digital, blindada para siempre.

¿Tienes una captura de chat, contrato o foto que quieres proteger? Envíala ahora. Nuestro motor aplicará un sello de *Integridad Post-Cuántica* y registro *Merkle Tree* para que nadie pueda negar su existencia ni alterar su contenido en el futuro.

✅ Privado | ✅ Inmutable | ✅ A prueba de futuro."""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa documentos (imágenes y PDFs) enviados por el usuario"""
    try:
        logger.info(f"📥 Archivo recibido de usuario {update.effective_user.id}")
        
        # Obtener el archivo
        if update.message.photo:
            # Es una foto
            logger.info("   Tipo: Foto (PHOTO)")
            file = await context.bot.get_file(update.message.photo[-1].file_id)
            file_type = "image"
            filename = f"chat_capture_{update.message.message_id}.jpg"
        elif update.message.document:
            # Es un documento (PDF, imagen, etc.)
            logger.info(f"   Tipo: Documento ({update.message.document.mime_type})")
            file = await context.bot.get_file(update.message.document.file_id)
            file_type = update.message.document.mime_type or "unknown"
            filename = update.message.document.file_name or f"document_{update.message.message_id}"
        else:
            await update.message.reply_text("❌ Por favor envía una imagen o PDF")
            return

        # Descargar el archivo
        file_bytes = await file.download_as_bytearray()
        file_bytes = bytes(file_bytes)

        # Calcular hash SHA-256
        file_hash = calculate_file_hash(file_bytes)
        file_size = len(file_bytes)

        # Generar certificado
        await update.message.reply_text("⏳ Procesando y certificando tu archivo...")
        logger.info(f"   Iniciando certificación de: {filename} ({file_size} bytes)")

        # Generar par de claves usando el motor criptográfico
        logger.info("   Generando par de claves híbrido...")
        keypair = crypto_engine.generar_par_claves_hibrido()
        logger.info("   ✓ Par de claves generado")

        # Crear certificado base
        cert_base = {
            'hash_sha256': file_hash,
            'timestamp_iso': datetime.now(timezone.utc).isoformat(),
            'archivo': {
                'nombre': filename,
                'tamano_bytes': file_size,
                'tipo': file_type
            },
            'claves_publicas': keypair.to_dict(),
            'fuente': 'telegram_bot',
            'user_id': str(update.effective_user.id)
        }

        # Serializar canónicamente
        logger.info("   Serializando certificado canónicamente...")
        mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)

        # Firmar con Ed25519 usando pqc_hybrid
        logger.info("   Firmando con Ed25519 (motor híbrido)...")
        dual_sig = crypto_engine.firmar_dual(mensaje_canonical, keypair)
        logger.info("   ✓ Firma dual generada")

        # Guardar en base de datos
        logger.info("   Guardando certificado en base de datos...")
        from aee.infrastructure.database import get_db
        db_gen = get_db()
        db = next(db_gen)
        try:
            cert_data = {
                'filename': filename,
                'hash_sha256': file_hash,
                'file_size_bytes': file_size,
                'ed25519_public': keypair.ed25519_public.hex(),
                'kyber_public': keypair.kyber_public.hex() if keypair.kyber_public else '',
                'signature_classic': dual_sig.signature_classic.hex(),
                'pqc_seal': dual_sig.pqc_seal.hex() if dual_sig.pqc_seal else None,
                'pqc_auth_tag': dual_sig.pqc_auth_tag.hex() if dual_sig.pqc_auth_tag else None,
                'metadata': {
                    'user_id': str(update.effective_user.id),
                    'username': update.effective_user.username,
                    'source': 'telegram_bot'
                },
                'timestamp_ntp': {
                    'timestamp_iso': datetime.now(timezone.utc).isoformat(),
                    'fuente': 'local'
                }
            }
            cert_model = CertificateRepository.create(db, cert_data, f"telegram_user_{update.effective_user.id}")
            cert_id_short = cert_model.id[:8].upper()  # Usar los primeros 8 caracteres del UUID
            logger.info(f"   ✓ Certificado guardado con ID: {cert_id_short}")
            AuditLogRepository.log(db, "TELEGRAM_CERTIFY", "SUCCESS", f"telegram_user_{update.effective_user.id}", 
                                 certificate_id=cert_model.id, response_status=200)
        finally:
            db.close()

        # Respuesta al usuario con formato específico
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        response_message = f"""✅ EVIDENCIA BLINDADA EXITOSAMENTE
━━━━━━━━━━━━━━━━━━━━
🆔 ID: {cert_id_short}
🔐 HASH: {file_hash}
📜 ESTADO: Inmutable & Post-Cuántico
🌐 VERIFICAR: {api_base_url}/api/v1/verify/{cert_id_short}
━━━━━━━━━━━━━━━━━━━━"""
        
        await update.message.reply_text(response_message, parse_mode=None)
        
        # Log de éxito en terminal
        logger.info("=" * 60)
        logger.info("✅ CERTIFICACIÓN EXITOSA")
        logger.info(f"   Usuario: {update.effective_user.id} (@{update.effective_user.username})")
        logger.info(f"   Archivo: {filename}")
        logger.info(f"   ID Certificado: {cert_id_short}")
        logger.info(f"   Hash SHA-256: {file_hash}")
        logger.info(f"   Tamaño: {file_size} bytes")
        logger.info("=" * 60)
        print(f"\n✅ CERTIFICACIÓN EXITOSA - ID: {cert_id_short} - Hash: {file_hash[:16]}...")

    except Exception as e:
        logger.error(f"Error procesando documento: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error al procesar el archivo: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto"""
    await update.message.reply_text(
        "📎 Por favor envía una imagen o PDF para certificar.\n\n"
        "Usa /start para ver las instrucciones."
    )


async def verify_bot_connection(application: Application):
    """Verifica que el bot esté conectado correctamente"""
    try:
        bot = application.bot
        bot_info = await bot.get_me()
        logger.info(f"Bot conectado: @{bot_info.username} - {bot_info.first_name}")
        print(f"Bot conectado: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"Error conectando bot: {e}")
        return False


def main():
    """Inicia el bot de Telegram @CertificadorOficialBot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado.")
        return

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Verificar conexión antes de iniciar polling
    async def post_init(app: Application):
        await verify_bot_connection(app)
    
    application.post_init = post_init

    # Iniciar bot
    logger.info("🤖 @CertificadorOficialBot iniciado y escuchando mensajes...")
    logger.info("✅ Bot en modo polling - Listo para recibir certificaciones")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

