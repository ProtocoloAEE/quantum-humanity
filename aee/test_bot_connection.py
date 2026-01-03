#!/usr/bin/env python3
"""Script de prueba para verificar conexión del bot de Telegram"""

import os
import sys

# Token del bot
TELEGRAM_BOT_TOKEN = '8551824212:AAG2ese5vIVrxUjrV7Uv4fPVEAAPa6Y6BQs'

try:
    from telegram import Bot
    
    print("🤖 Probando conexión con @CertificadorOficialBot...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Obtener información del bot
    bot_info = bot.get_me()
    
    print(f"✅ Bot conectado exitosamente!")
    print(f"   Nombre: {bot_info.first_name}")
    print(f"   Username: @{bot_info.username}")
    print(f"   ID: {bot_info.id}")
    print(f"\n✅ El bot está listo para recibir mensajes (polling)")
    print(f"   Ejecuta: python telegram_bot.py")
    
except ImportError:
    print("❌ Error: python-telegram-bot no está instalado")
    print("   Instala con: pip install python-telegram-bot")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)

