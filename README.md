# 🛡️ Protocolo AEE - v2.1 HARDENED

## ⚖️ Evidencia Digital
Herramienta forense de certificación con firma Ed25519 y consenso NTP.

## 🛠️ Uso
from aee.core import EvidenceProtocol
p = EvidenceProtocol('tu@email.com')
p.initialize()
cert = p.certify_file('prueba.txt')
