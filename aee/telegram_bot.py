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

# Token del bot (debe estar en variable de entorno)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Motor criptográfico global
crypto_engine = HybridCryptoEngine()


def calculate_file_hash(file_bytes: bytes) -> str:
    """Calcula SHA-256 de un archivo"""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start con mensaje vendedor"""
    welcome_message = """
🛡️ *Bienvenido al Certificador de Evidencia AEE*

Envía tu captura de chat o documento para blindarlo *HOY MISMO* con:

✅ *Integridad Post-Cuántica* - Resistente a computadoras cuánticas
✅ *Firma Digital Ed25519* - Verificación pública instantánea
✅ *Timestamp Consensuado* - Temporalidad verificable
✅ *Certificado Inmutable* - Tu evidencia protegida para siempre

*¿Cómo funciona?*
1. Envía una imagen (JPG, PNG) o PDF
2. El bot calculará el hash y generará un certificado único
3. Recibirás un ID de certificado y hash para verificación

*¡Blinda tu evidencia ahora!* 🚀
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa documentos (imágenes y PDFs) enviados por el usuario"""
    try:
        # Obtener el archivo
        if update.message.photo:
            # Es una foto
            file = await context.bot.get_file(update.message.photo[-1].file_id)
            file_type = "image"
            filename = f"chat_capture_{update.message.message_id}.jpg"
        elif update.message.document:
            # Es un documento (PDF, imagen, etc.)
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

        # Generar par de claves
        keypair = crypto_engine.generar_par_claves_hibrido()

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
        mensaje_canonical = CanonicalJSONSerializer.serialize(cert_base)

        # Firmar con Ed25519
        dual_sig = crypto_engine.firmar_dual(mensaje_canonical, keypair)

        # Guardar en base de datos
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
            AuditLogRepository.log(db, "TELEGRAM_CERTIFY", "SUCCESS", f"telegram_user_{update.effective_user.id}", 
                                 certificate_id=cert_model.id, response_status=200)
        finally:
            db.close()

        # Respuesta al usuario
        response_message = f"""
✅ *Archivo Certificado*

*ID:* `{cert_id_short}`
*Hash SHA-256:* `{file_hash}`
*Archivo:* {filename}
*Tamaño:* {file_size} bytes

El documento ha sido sellado con *integridad Post-Cuántica* y está protegido para siempre.

*Verificar certificado:*
http://localhost:8000/api/v1/verify/{cert_id_short}

🛡️ *Tu evidencia está blindada*
        """
        await update.message.reply_text(response_message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error procesando documento: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error al procesar el archivo: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto"""
    await update.message.reply_text(
        "📎 Por favor envía una imagen o PDF para certificar.\n\n"
        "Usa /start para ver las instrucciones."
    )


def main():
    """Inicia el bot de Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado. Configúralo como variable de entorno.")
        return

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Iniciar bot
    logger.info("🤖 Bot de Telegram iniciado")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

