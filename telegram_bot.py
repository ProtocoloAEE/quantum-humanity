# MVP - AEE Telegram Certification Bot
# Refactored to use HybridCryptoEngine and handle file processing.

import logging
import os
import asyncio
import uvicorn
import uuid
import sys
import io

from fastapi import FastAPI, HTTPException
from telegram import Update, File
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# AEE Protocol Imports - Using the refactored engine
from aee.pqc_hybrid import HybridCryptoEngine

# --- Configuration and Globals ---

# Fix Unicode errors in Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Telegram Bot Token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN environment variable not found. The bot will not start.")

# In-memory database for the MVP
CERTIFICATE_DB = {}

# Instantiate the cryptographic engine
crypto_engine = HybridCryptoEngine()


# --- FastAPI Application ---

app = FastAPI(
    title="AEE Verification API",
    description="API for verifying AEE certificates.",
    version="1.3.0"
)

@app.get("/")
def read_root():
    return {"status": "AEE Verification API is running"}

@app.get("/verify/{cert_id}")
async def verify_certificate(cert_id: str):
    """Verifies if a certificate ID is valid and returns its data."""
    logger.info(f"Received verification request for ID: {cert_id}")
    certificate = CERTIFICATE_DB.get(cert_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate ID not found.")
    
    return {
        "status": "VALID",
        "certificate_id": cert_id,
        "certificate_data": certificate
    }


# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text("Bienvenido al Certificador de Evidencia. Envía tu captura de chat para blindarla hoy mismo.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming documents and photos for certification."""
    message = update.message
    # Works for both photos (message.photo) and documents (message.document)
    attachment = message.effective_attachment

    if message.photo:
        # For photos, get the largest one
        file_id = attachment[-1].file_id
    else:
        file_id = attachment.file_id
    
    try:
        sent_message = await message.reply_text("Procesando evidencia...")
        
        new_file: File = await context.bot.get_file(file_id)
        file_bytes = await new_file.download_as_bytearray()
        
        logger.info(f"Processing file of size: {len(file_bytes)} bytes")
        
        # Use the crypto engine to sign the evidence
        signature_result = crypto_engine.sign_evidence(bytes(file_bytes))
        
        # Generate a unique ID for this certificate
        cert_id = uuid.uuid4().hex
        
        # Store the certificate data in our in-memory DB
        CERTIFICATE_DB[cert_id] = signature_result.to_dict()
        
        logger.info(f"Successfully certified file. ID: {cert_id}, Hash: {signature_result.hash}")
        
        # Format the response message
        response_text = (
            f"✅ EVIDENCIA BLINDADA\n\n"
            f"**ID de Certificado:** `{cert_id}`\n"
            f"**Hash (SHA-256):** `{signature_result.hash}`\n"
            f"**Algoritmo:** `{signature_result.algorithm}`\n\n"
            f"El documento ha sido sellado con integridad Post-Cuántica."
        )
        
        await sent_message.edit_text(response_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Failed to process file: {e}", exc_info=True)
        await message.reply_text(f"Ocurrió un error al procesar el archivo: {e}")


# --- Main Application Setup ---

async def run_bot():
    """Initializes and runs the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Cannot start bot: TELEGRAM_BOT_TOKEN is not set.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    # Enable the handler for Documents (PDFs) and Photos
    doc_and_photo_handler = MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document)
    application.add_handler(doc_and_photo_handler)
    
    bot_info = await application.bot.get_me()
    logger.info(f"🤖 @{bot_info.username} iniciado. Listening for evidence...")
    await application.run_polling()


async def main():
    """Runs the Telegram bot."""
    await run_bot()


if __name__ == "__main__":
    logger.info("Starting AEE Bot...")
    if not TELEGRAM_BOT_TOKEN:
        print("\nFATAL: TELEGRAM_BOT_TOKEN is not set.")
        print("Please create a .env file and add: TELEGRAM_BOT_TOKEN='your-token-here'")
        print("Or set it as an environment variable.\n")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Shutting down bot.")
        except Exception as e:
            logger.critical(f"Bot failed with a critical error: {e}", exc_info=True)