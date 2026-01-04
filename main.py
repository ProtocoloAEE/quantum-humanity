#!/usr/bin/env python3
"""
Punto de entrada principal para AEE Bot
Acta de Evidencia Electrónica v3.0
"""

import sys
import os
import logging

# Configurar logging antes de importar módulos
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Importar y ejecutar bot
from aee.telegram_bot import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBot detenido por el usuario")
    except Exception as e:
        print(f"\n\nError fatal: {e}")
        raise
