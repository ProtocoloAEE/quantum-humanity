#!/usr/bin/env python3
import sys
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from aee.telegram_bot import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Bot detenido")
    except Exception as e:
        print(f"Error: {e}")
        raise
