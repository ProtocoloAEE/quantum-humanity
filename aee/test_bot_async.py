#!/usr/bin/env python3
"""Script de prueba asíncrono para verificar conexión del bot"""

import asyncio
import os

TELEGRAM_BOT_TOKEN = '8551824212:AAG2ese5vIVrxUjrV7Uv4fPVEAAPa6Y6BQs'

async def test_connection():
    try:
        from telegram import Bot
        
        print("Probando conexión con @CertificadorOficialBot...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Obtener información del bot (async correctamente)
        bot_info = await bot.get_me()
        
        print(f"Bot conectado: @{bot_info.username}")
        print(f"Nombre: {bot_info.first_name}")
        print(f"ID: {bot_info.id}")
        print("\n✅ Conexión exitosa!")
        return True
        
    except ImportError:
        print("❌ Error: python-telegram-bot no está instalado")
        return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())

