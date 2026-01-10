import logging
import hashlib
import re
import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

from aee.database import DatabaseManager, calculate_file_hash
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
    await update.message.reply_text(
        "**AEE Bot - Preservación Digital**\n\n"
        "Envía archivos para calcular hash SHA-256 con metadata.\n"
        "Usa `/verificar` respondiendo a un mensaje con hash.\n"
        "Comandos: `/start`, `/verificar`, `/historial`",
        parse_mode="Markdown"
    )


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuario {update.effective_user.id} envió /verificar")
    
    try:
        message = update.message
        
        if not message.reply_to_message:
            await message.reply_text("Responde a un mensaje con hash usando `/verificar`.", parse_mode="Markdown")
            return
        
        original_text = message.reply_to_message.text
        hash_match = re.search(r'([a-fA-F0-9]{64})', re.sub(r'\s+', '', original_text))
        
        if not hash_match:
            await message.reply_text("No se encontró hash SHA-256 válido.", parse_mode="Markdown")
            return
        
        original_hash = hash_match.group(1)
        
        # VALIDACIÓN 3: ¿El mensaje actual contiene archivo?
        if not (message.photo or message.document):
            await message.reply_text("Envía una foto o documento para verificar.", parse_mode="Markdown")
            return
        
        # Descargar archivo
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
            else:
                file_id = message.document.file_id
            
            new_file = await context.bot.get_file(file_id)
            file_content = await new_file.download_as_bytearray()
            
        except Exception as e:
            logger.exception(f"Error descargando: {e}")
            await message.reply_text(f"Error al descargar: {str(e)}", parse_mode="Markdown")
            return
        
        # Buscar registro original por hash
        original_record = DatabaseManager.get_preservation_by_hash(original_hash)
        if not original_record:
            await message.reply_text("Hash no encontrado en registros.", parse_mode="Markdown")
            return
        
        # Calcular hash del nuevo archivo con metadata original
        try:
            new_hash = calculate_file_hash(
                file_content=file_content,
                timestamp=original_record.timestamp_utc,
                user_id=original_record.user_id,
                device_id=original_record.device_id
            )
            
        except Exception as e:
            logger.exception(f"Error calculando hash: {e}")
            await message.reply_text(f"Error al procesar: {str(e)}", parse_mode="Markdown")
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
    logger.info(f"Usuario {update.effective_user.id} envió archivo")
    
    try:
        message = update.message
        user_id = str(update.effective_user.id)
        
        if message.text and message.text.startswith('/'):
            return
        
        # Determinar tipo de archivo
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            mime_type = message.document.mime_type
        elif message.photo:
            file_id = message.photo[-1].file_id
            file_name = f"photo_{datetime.now(timezone.utc).isoformat()}.jpg"
            mime_type = "image/jpeg"
        else:
            await message.reply_text("Envía una foto o documento.", parse_mode="Markdown")
            return
        
        # Descargar archivo
        try:
            new_file = await context.bot.get_file(file_id)
            file_content = await new_file.download_as_bytearray()
        except Exception as e:
            logger.exception(f"Error descargando: {e}")
            await message.reply_text(f"Error al descargar: {str(e)}", parse_mode="Markdown")
            return
        
        # Registrar preservación
        try:
            preservation = DatabaseManager.add_preservation(
                file_content=file_content,
                file_name=file_name,
                mime_type=mime_type,
                user_id=user_id
            )
            file_hash = preservation.file_hash
        except ValueError as e:
            await message.reply_text(f"⚠️ {str(e)}", parse_mode="Markdown")
            return
        except Exception as e:
            logger.exception(f"Error registro: {e}")
            await message.reply_text(f"Error: {str(e)}", parse_mode="Markdown")
            return
        
        # ÉXITO: Enviar reporte con botón de certificado
        reporte = (
            f"**PRESERVACIÓN TÉCNICA REGISTRADA**\n\n"
            f"**Tipo de archivo:** {file_type.upper()}\n"
            f"**Tamaño:** {len(file_content):,} bytes\n"
            f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}Z\n"
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
    
    # Cargar variables de entorno
    load_dotenv()
    
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    logger.info(f"Iniciando AEE Bot con token: {TOKEN[:20] if TOKEN else None}...")
    
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
