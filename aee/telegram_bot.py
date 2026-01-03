import os
import sys
import logging
import hashlib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from aee.pqc_hybrid import HybridCryptoEngine

# Corrección de terminal para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8551824212:AAG2ese5vIVrxUjrV7Uv4fPVEAAPa6Y6BQs"
crypto_engine = HybridCryptoEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ Protocolo AEE v1.3 Online. Envíe una imagen para preservar.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attachment = update.message.photo[-1] if update.message.photo else update.message.document
    if not attachment: return

    msg = await update.message.reply_text("⏳ Procesando preservación...")
    try:
        file = await context.bot.get_file(attachment.file_id)
        file_bytes = await file.download_as_bytearray()
        cert_obj = crypto_engine.sign_evidence(bytes(file_bytes))
        data = cert_obj.to_dict()
        
        response = (
            "📄 REPORTE DE PRESERVACIÓN DIGITAL\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔍 HASH SHA-256:\n{data['hash']}\n\n"
            f"📅 FECHA: {data['timestamp']}\n"
            "⚖️ DISCLAIMER: Preservación técnica de parte."
        )
        await msg.edit_text(response)
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("❌ Error al procesar el archivo.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_document))
    logger.info("Bot ONLINE")
    app.run_polling()