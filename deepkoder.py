import os
import sys
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import re

class SupremeLogger:
    COLORS = {'HEADER': '\033[1;36m', 'INFO': '\033[92m', 'WARNING': '\033[93m', 'ERROR': '\033[91m', 'ENDC': '\033[0m'}
    def log(self, level, msg):
        print(f"{self.COLORS.get(level, '')}[{level}] {msg}{self.COLORS['ENDC']}")
    def section(self, title):
        print(f"\n{self.COLORS['HEADER']}{'='*60}\n{title}\n{'='*60}{self.COLORS['ENDC']}")

class DeepkoderLite:
    def __init__(self):
        self.root = Path(os.getcwd())
        self.logger = SupremeLogger()
    
    def run(self):
        self.logger.section("🔍 AUDITORÍA DE CALIDAD AEE-PROTOCOL")
        files = list(self.root.rglob("*.py"))
        total_lines = 0
        self.logger.log("INFO", f"Archivos detectados: {len(files)}")
        
        for f in files:
            if ".venv" in str(f) or "__pycache__" in str(f): continue
            with open(f, 'r', encoding='utf-8', errors='ignore') as content:
                lines = content.readlines()
                total_lines += len(lines)
                self.logger.log("INFO", f"📄 {f.name}: {len(lines)} líneas")

        score = 100
        if not (self.root / "README.md").exists(): score -= 10
        if not (self.root / "requirements.txt").exists(): score -= 10
        
        self.logger.section("📊 RESULTADOS FINALES")
        print(f"PUNTUACIÓN DE ESTRUCTURA: {score}/100")
        print(f"LÍNEAS DE CÓDIGO TOTALES: {total_lines}")
        
        if score == 100:
            self.logger.log("INFO", "ESTADO: PROYECTO PROFESIONAL")
        else:
            self.logger.log("WARNING", "ESTADO: NECESITA DOCUMENTACIÓN (README/REQUIREMENTS)")

if __name__ == "__main__":
    DeepkoderLite().run()
