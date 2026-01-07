"""
aee/telegram_bot.py
Bot de Telegram para AEE - Acta de Evidencia Electrónica
Preservación digital con certificación criptográfica.
"""

import logging
import hashlib
import re
import os
import asyncio
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

from aee.database import DatabaseManager
from aee.certificate import generate_certificate

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

PRESERVATION_CACHE = {}  # Para vincular callbacks con preservaciones


# ============================================================================
# HANDLERS DE COMANDOS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja el comando /start.
    Presenta el bot y sus capacidades.
    """
    logger.info(f"Usuario {update.effective_user.id} envió /start")
    
    start_message = (
        "**Bienvenido a AEE Bot - Acta de Evidencia Electrónica**\n\n"
        "Soy un bot especializado en certificación criptográfica digital.\n\n"
        "**¿Qué puedo hacer?**\n"
        "Genero hashes SHA-256 de tus archivos (fotos, documentos)\n"
        "Emito certificados PDF profesionales de preservación\n"
        "Valido la integridad comparando archivos\n\n"
        "**Comandos disponibles:**\n"
        "`/start` - Muestra este mensaje\n"
        "`/verificar` - Compara integridad de dos archivos\n"
        "`/historial` - Lista tus preservaciones recientes\n\n"
        "**Cómo empezar:**\n"
        "1. Envía una foto o documento\n"
        "2. Recibirás el hash SHA-256\n"
        "3. Descarga tu certificado PDF\n"
        "4. Usa `/verificar` para validar otros archivos\n\n"
        "*Sistema de preservación digital con firma criptográfica*"
    )
    
    await update.message.reply_text(start_message, parse_mode="Markdown")


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Verifica la integridad de un archivo comparándolo con uno anterior.
    """
    logger.info(f"Usuario {update.effective_user.id} envió comando /verificar")
    
    try:
        message = update.message
        
        # VALIDACIÓN 1: ¿Está respondiendo a un mensaje previo?
        if not message.reply_to_message:
            logger.warning("verify_command: No hay mensaje anterior")
            await message.reply_text(
                "Debes responder a un mensaje anterior con el comando `/verificar`.\n\n"
                "Ejemplo: Responde el mensaje que contiene el hash con `/verificar`.",
                parse_mode="Markdown"
            )
            return
        
        original_text = message.reply_to_message.text
        logger.debug(f"Texto del mensaje anterior: {original_text[:100]}...")
        
        # VALIDACIÓN 2: ¿El mensaje anterior contiene un hash?
        # Extraer cualquier hash SHA-256 válido aunque esté partido en líneas
        clean_text = re.sub(r'\s+', '', original_text)
        hash_match = re.search(r'([a-fA-F0-9]{64})', clean_text)

        if not hash_match:
            logger.warning("verify_command: No se encontró patrón de hash")
            await message.reply_text(
                "No se encontró un hash SHA-256 válido en el mensaje original.",
                parse_mode="Markdown"
            )
            return

        original_hash = hash_match.group(1)
        logger.info(f"Hash original reconstruido correctamente: {original_hash}")
        
        # VALIDACIÓN 3: ¿El mensaje actual contiene una foto?
        if not message.photo:
            logger.warning("verify_command: Sin foto en mensaje actual")
            await message.reply_text(
                "Debes enviar una foto o documento junto con `/verificar`.",
                parse_mode="Markdown"
            )
            return
        
        # VALIDACIÓN 4: Descargar y calcular hash
        try:
            file_id = message.photo[-1].file_id
            new_file = await context.bot.get_file(file_id)
            file_content = await new_file.download_as_bytearray()
            new_hash = hashlib.sha256(file_content).hexdigest()
            
            logger.info(f"Hash nuevo calculado: {new_hash}")
            
        except Exception as e:
            logger.exception(f"Error descargando archivo: {type(e).__name__}: {e}")
            await message.reply_text(
                f"Error al descargar el archivo: {str(e)}",
                parse_mode="Markdown"
            )
            return
        
        # VERIFICACIÓN FINAL
        if original_hash == new_hash:
            logger.info("Hashes coinciden")
            await message.reply_text(
                "**INTEGRIDAD CONFIRMADA**\n\n"
                f"El archivo es idéntico al original.\n"
                f"`{new_hash}`",
                parse_mode="Markdown"
            )
        else:
            logger.warning(f"Hashes NO coinciden!")
            await message.reply_text(
                "**INTEGRIDAD VIOLADA**\n\n"
                f"El archivo ha sido modificado.\n\n"
                f"Original: `{original_hash}`\n"
                f"Actual:   `{new_hash}`",
                parse_mode="Markdown"
            )
    
    except Exception as e:
        logger.exception(f"Error en verify_command: {type(e).__name__}: {e}")
        await message.reply_text(
            f"Error: {str(e)}",
            parse_mode="Markdown"
        )


async def historial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el historial de preservaciones del usuario.
    """
    logger.info(f"Usuario {update.effective_user.id} envió comando /historial")
    
    try:
        user_id = str(update.effective_user.id)
        
        # Obtener preservaciones del usuario desde BD
        records = DatabaseManager.get_preservations_by_user(user_id)
        
        if not records:
            await update.message.reply_text(
                "No tienes preservaciones registradas aún.",
                parse_mode="Markdown"
            )
            return
        
        # Construir mensaje
        historial_text = f"**Tu historial ({len(records)} preservaciones):**\n\n"
        
        for i, record in enumerate(records[-5:], 1):  # Últimas 5
            timestamp = record.timestamp_utc.strftime("%Y-%m-%d %H:%M:%S")
            historial_text += (
                f"{i}. **ID {record.id}** - {record.file_name}\n"
                f"   Tamaño: {record.file_size/1024:.1f} KB | {timestamp}\n"
                f"   Hash: `{record.file_hash[:32]}...`\n\n"
            )
        
        await update.message.reply_text(historial_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.exception(f"Error en historial_command: {type(e).__name__}: {e}")
        await message.reply_text(
            f"Error al obtener historial: {str(e)}",
            parse_mode="Markdown"
        )


# ============================================================================
# HANDLERS DE MENSAJES
# ============================================================================

async def preserve_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Preserva un archivo (foto o documento) calculando su hash SHA-256.
    Registra en BD y ofrece descargar certificado PDF.
    """
    logger.info(f"Usuario {update.effective_user.id} envió archivo")
    
    try:
        message = update.message
        user_id = str(update.effective_user.id)
        
        # VALIDACIÓN 1: No procesar comandos
        if message.text and message.text.startswith('/'):
            logger.debug(f"Ignorando comando: {message.text}")
            return
        
        # VALIDACIÓN 2: Determinar tipo de archivo
        file_id = None
        file_type = None
        file_name = None
        mime_type = None
        
        if message.document:
            file_id = message.document.file_id
            file_type = "documento"
            file_name = message.document.file_name
            mime_type = message.document.mime_type
            logger.debug(f"Tipo: Documento - MIME: {mime_type}")
            
        elif message.photo:
            if len(message.photo) == 0:
                logger.warning("photo existe pero está vacía")
                await message.reply_text("No se recibió imagen válida.")
                return
            
            file_id = message.photo[-1].file_id
            file_type = "foto"
            file_name = f"photo_{datetime.utcnow().isoformat()}.jpg"
            mime_type = "image/jpeg"
            logger.debug(f"Tipo: Foto")
            
        else:
            logger.info("Mensaje sin foto ni documento")
            await message.reply_text(
                "Por favor, envía una **foto** o **documento**.",
                parse_mode="Markdown"
            )
            return
        
        if not file_id:
            logger.error("file_id es None")
            await message.reply_text("Error: No se pudo extraer el ID del archivo.")
            return
        
        logger.info(f"File ID: {file_id[:20]}... (tipo: {file_type})")
        
        # VALIDACIÓN 3: Descargar archivo
        try:
            new_file = await context.bot.get_file(file_id)
            file_content = await new_file.download_as_bytearray()
            logger.info(f"Archivo descargado - Tamaño: {len(file_content)} bytes")
            
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {e}")
            await message.reply_text(
                "El archivo no está disponible en los servidores de Telegram.",
                parse_mode="Markdown"
            )
            return
            
        except Exception as e:
            logger.exception(f"Error descargando archivo: {type(e).__name__}: {e}")
            await message.reply_text(
                f"Error al descargar: {type(e).__name__}",
                parse_mode="Markdown"
            )
            return
        
        # VALIDACIÓN 4: Calcular hash SHA-256
        try:
            file_hash = hashlib.sha256(file_content).hexdigest()
            logger.info(f"Hash SHA-256 calculado: {file_hash}")
            
        except Exception as e:
            logger.exception(f"Error calculando SHA-256: {type(e).__name__}: {e}")
            await message.reply_text(f"Error al procesar el archivo: {str(e)}")
            return
        
        # VALIDACIÓN 5: Registrar en BD
        try:
            preservation = DatabaseManager.add_preservation(
                file_hash=file_hash,
                file_name=file_name,
                mime_type=mime_type,
                file_size=len(file_content),
                user_id=user_id
            )
            
            logger.info(f"Preservación registrada: ID={preservation.id}")
            
            # Guardar en cache para callbacks
            PRESERVATION_CACHE[f"cert_{preservation.id}"] = preservation.id
            
        except ValueError as e:
            logger.warning(f"Validación fallida: {e}")
            await message.reply_text(
                f"⚠️ {str(e)}",
                parse_mode="Markdown"
            )
            return
            
        except Exception as e:
            logger.exception(f"Error en BD: {type(e).__name__}: {e}")
            await message.reply_text(
                f"Error al registrar preservación: {str(e)}",
                parse_mode="Markdown"
            )
            return
        
        # ÉXITO: Enviar reporte con botón de certificado
        reporte = (
            f"**PRESERVACIÓN TÉCNICA REGISTRADA**\n\n"
            f"**Tipo de archivo:** {file_type.upper()}\n"
            f"**Tamaño:** {len(file_content):,} bytes\n"
            f"**Timestamp:** {datetime.utcnow().isoformat()}Z\n"
            f"**Algoritmo:** SHA-256\n\n"
            f"**Hash:** `{file_hash}`\n\n"
            f"*Puedes usar `/verificar` para comparar integridad*"
        )
        
        # Crear botón de descarga de certificado
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Descargar Certificado PDF",
                    callback_data=f"cert_{preservation.id}"
                )
            ]
        ])
        
        await message.reply_text(reporte, parse_mode="Markdown", reply_markup=keyboard)
        logger.info("Reporte enviado con botón de certificado")
        
    except Exception as e:
        logger.exception(f"Error en preserve_message: {type(e).__name__}: {e}")
        await message.reply_text(
            f"**ERROR INESPERADO**\n\n`{type(e).__name__}: {str(e)}`",
            parse_mode="Markdown"
        )


# ============================================================================
# CALLBACK HANDLER (BOTONES INLINE)
# ============================================================================

async def handle_certificate_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja la descarga de certificado PDF cuando se presiona el botón.
    """
    query = update.callback_query
    user_id = str(update.effective_user.id)
    
    logger.info(f"Usuario {user_id} solicitó certificado: {query.data}")
    
    try:
        # Extraer ID de preservación
        preservation_id = int(query.data.split('_')[1])
        
        # Validar que el usuario sea el propietario
        record = DatabaseManager.get_preservation_by_id(preservation_id)
        
        if not record:
            await query.answer("Certificado no encontrado.", show_alert=True)
            return
        
        if record.user_id != user_id:
            await query.answer("No tienes permiso para descargar este certificado.", show_alert=True)
            logger.warning(f"Intento de acceso no autorizado: user={user_id}, owner={record.user_id}")
            return
        
        # Notificar al usuario
        await query.answer("Generando certificado PDF...", show_alert=False)
        
        logger.info(f"Generando certificado para preservación ID={preservation_id}")
        
        # Generar certificado
        try:
            logger.info("🔧 Iniciando generación de certificado...")
            pdf_path = generate_certificate(record)
            
            # Verificación redundante (doble check)
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF no encontrado en {pdf_path}")
            
            logger.info(f"📤 Enviando PDF desde: {pdf_path}")
            
            # Enviar documento por Telegram (MÉTODO CORRECTO)
            with open(pdf_path, "rb") as pdf_file:
                await query.message.reply_document(
                    document=pdf_file,
                    filename=f"certificado_{record.file_hash[:8]}.pdf",
                    caption=(
                        f"✅ **Certificado de Preservación Digital**\n\n"
                        f"Hash: `{record.file_hash[:32]}...`\n"
                        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    ),
                    parse_mode="Markdown"
                )
            
            logger.info(f"✅ Certificado enviado exitosamente a chat {user_id}")
            
        except FileNotFoundError as e:
            logger.error(f"❌ Archivo no encontrado: {e}")
            await query.answer("❌ Error: No se pudo generar el certificado PDF", show_alert=True)
            await query.message.reply_text(
                "❌ Error: No se pudo generar el certificado PDF. "
                "Por favor contacta al administrador.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ Error crítico al procesar certificado: {e}", exc_info=True)
            await query.answer("❌ Error inesperado al generar el certificado", show_alert=True)
            await query.message.reply_text(
                f"❌ Error inesperado al generar el certificado.\n\n"
                f"`{type(e).__name__}: {str(e)}`",
                parse_mode="Markdown"
            )
        
    except ValueError as e:
        logger.warning(f"Validación fallida: {e}")
        await query.answer(f"Error: {str(e)}", show_alert=True)
        
    except Exception as e:
        logger.exception(f"Error en handle_certificate_download: {type(e).__name__}: {e}")
        await query.answer(f"Error: {type(e).__name__}", show_alert=True)


# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja errores globales.
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"Error en el sistema: {type(context.error).__name__}",
                parse_mode="Markdown"
            )
        except:
            pass


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Inicializa la aplicación de Telegram.
    """
    # Inicializar base de datos
    from aee.database import init_database
    init_database()
    
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8551824212:AAHk_Yuo333K6Kl_fj3tVu8uV72_s0wjKtc")
    
    logger.info(f"Iniciando AEE Bot con token: {TOKEN[:20]}...")
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Registrar handlers
        app.add_handler(CommandHandler('start', start_command))
        app.add_handler(CommandHandler('verificar', verify_command))
        app.add_handler(CommandHandler('historial', historial_command))
        
        # Handler para fotos y documentos
        app.add_handler(MessageHandler(
            filters.PHOTO | filters.Document.ALL,
            preserve_message
        ))
        
        # Handler de callbacks (botones inline)
        app.add_handler(CallbackQueryHandler(handle_certificate_download, pattern=r"^cert_\d+$"))
        
        # Error handler
        app.add_error_handler(error_handler)
        
        logger.info("Todos los handlers registrados")
        logger.info("--- AEE BOT INICIADO Y LISTO ---")
        
        app.run_polling(close_loop=False, allowed_updates=None)
        
    except Exception as e:
        logger.exception(f"Error fatal: {type(e).__name__}: {e}")
        raise


if __name__ == '__main__':
    main()
