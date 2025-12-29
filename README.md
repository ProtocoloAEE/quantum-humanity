# 🔐 Protocolo AEE v2.0 - Auditoría Ética y Evidencia

**Sistema open-source de certificación soberana para evidencia digital con potencial validez legal**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Licencia AGPLv3](https://img.shields.io/badge/Licencia-AGPLv3-green.svg)](LICENSE)
[![Beta](https://img.shields.io/badge/Estado-Beta-yellow.svg)]()

---

## ⚠️ IMPORTANTE: Lea esto primero

Esta herramienta está en **fase beta**.

- No previene edición **antes** de la captura.
- No reemplaza un peritaje judicial oficial.
- No garantiza aceptación automática como prueba en juicio.
- Úsela como **apoyo complementario** y siempre consulte con un abogado especializado.

---

## 🎯 ¿Qué hace el Protocolo AEE?

Permite a cualquier ciudadano generar evidencia digital con mayor integridad y trazabilidad:

- Calcula hash inmutable (SHA-256)
- Obtiene timestamp por consenso de múltiples servidores NTP oficiales
- Firma digitalmente con Ed25519 (claves seguras con entropía real)
- Genera certificado JSON verificable por cualquiera

**Ideal como apoyo en denuncias por estafas digitales, fraudes o manipulación.**

---

## ✨ Características v2.0

- Criptografía segura (Ed25519 + keyring del sistema operativo)
- Timestamp robusto (consenso NTP multi-servidor)
- Repo limpio y estructurado
- Disclaimer legal claro
- Preparado para futura integración con BFA.ar (Blockchain Federal Argentina)

---

## 🚀 Instalación y uso rápido

```bash
git clone https://github.com/ProtocoloAEE/quantum-humanity.git
cd quantum-humanity
pip install -r requirements.txt
Pythonfrom aee.core import EvidenceProtocol

protocol = EvidenceProtocol("tu@email.com")
cert = protocol.certify_file("captura_estafa.png", description="Conversación antes del bloqueo")
print("Certificado generado:", cert["certification_id"])

📁 Estructura del proyecto
textquantum-humanity/
├── aee/               # Código fuente principal
├── tests/             # Pruebas unitarias
├── docs/              # Documentación adicional
├── certificados/      # Certificados generados (creado automáticamente)
├── examples/          # Ejemplos de uso
├── requirements.txt
├── README.md
└── LICENSE

⚖️ Consideraciones legales (Argentina)
Diseñado como apoyo para:

Ley 25.506 (Firma Electrónica)
Ley 24.240 (Defensa del Consumidor)
Código Penal (estafas y fraudes)

Genera firma electrónica simple con integridad y autenticidad técnica.

🔜 Próximas mejoras

Integración BFA.ar (timestamp oficial argentino)
Generación automática de PDF para jueces
Interfaz gráfica simple
App móvil


🤝 Contribuir
¡Toda ayuda es bienvenida! Abre un issue o pull request.


📜 Licencia
AGPLv3 – Código abierto, auditable y modificable.
La soberanía digital se ejerce con transparencia, código bueno y comunidad.
Gracias a r/argentina por el feedback que hizo posible esta v2.0.
Franco Luciano Carricondo
Diciembre 2025
