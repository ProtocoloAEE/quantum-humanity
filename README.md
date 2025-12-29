# 🔐 Protocolo AEE (Auditoría Ética y Evidencia) v2.0

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Licencia AGPLv3](https://img.shields.io/badge/Licencia-AGPLv3-green.svg)
![Status Beta](https://img.shields.io/badge/Status-Beta-yellow.svg)

**Sistema de certificación soberana para evidencia digital con validez legal potencial**

---

## ⚠️ IMPORTANTE: LEA PRIMERO

**Esta herramienta está en fase BETA.**

- No previene edición ANTES de la captura.
- No reemplaza peritaje judicial oficial.
- No garantiza aceptación automática en juicio.
- Úsela como apoyo complementario y siempre consulte con un abogado.

---

## 🎯 ¿Qué es el Protocolo AEE?

El Protocolo AEE permite a cualquier ciudadano generar evidencia digital con mayor integridad y trazabilidad, útil como apoyo en denuncias por estafas, fraudes o manipulación digital.

**No es prueba legal automática, pero dificulta la alteración posterior y proporciona elementos verificables.**

---

## ✨ Características Principales (v2.0)

### 🛡️ Blindaje Técnico y Legal
- **Sellado de Tiempo Auditable**: Consenso de múltiples servidores NTP oficiales (Google, Cloudflare, pool.ntp.org, etc.) para fecha cierta.
- **Hash Inmutable**: SHA-256 del archivo completo.
- **Firma Digital Real**: Ed25519 con generación de claves aleatorias (entropía verdadera) y almacenamiento seguro en keyring del sistema operativo.
- **Certificado JSON Verificable**: Incluye hash, timestamp, firma, clave pública e instrucciones de verificación.

### 🔐 Criptografía Segura
- Claves privadas nunca derivadas de DNI u otros datos públicos.
- Firmas verificables offline por cualquiera.
- Preparado para integración futura con BFA.ar (Blockchain Federal Argentina).

### 👤 Soberanía Ciudadana
- Funciona 100% offline.
- No envía datos a servidores externos.
- Código abierto y auditable.

---

## 🚀 Instalación y Uso Rápido

```bash
git clone https://github.com/ProtocoloAEE/quantum-humanity.git
cd quantum-humanity
pip install -r requirements.txt
Pythonfrom aee.core import EvidenceProtocol

# Inicializar (genera claves si no existen)
protocol = EvidenceProtocol("tu@email.com")

# Certificar un archivo
cert = protocol.certify_file("captura_estafa.png", description="Conversación antes del bloqueo")

print("Certificado generado:", cert["certification_id"])

📁 Estructura del Proyecto
textquantum-humanity/
├── aee/                  # Código fuente principal
├── tests/                # Pruebas unitarias
├── docs/                 # Documentación adicional
├── certificados/         # Certificados generados (creado automáticamente)
├── requirements.txt
├── README.md
└── LICENSE

⚖️ Consideraciones Legales (Argentina)
Diseñado como apoyo para:

Ley 25.506 (Firma Electrónica)
Ley 24.240 (Defensa del Consumidor)
Código Penal (estafas, fraudes)

Genera firma electrónica simple con integridad y autenticidad técnica. Para firma digital calificada, usar servicios oficiales (AFIP, ONTI, etc.).

🔜 Próximas Mejoras

Integración BFA.ar (timestamp oficial argentino)
Generación automática de PDF legible para jueces
Interfaz gráfica simple
App móvil


🤝 Contribuir
¡Toda ayuda es bienvenida! Lee CONTRIBUTING.md (próximamente) para:

Reportar bugs
Sugerir mejoras
Enviar pull requests


📞 Contacto

Issues en GitHub (bugs técnicos)


📜 Licencia
AGPLv3 – Código abierto, auditable y modificable.
La soberanía digital se ejerce con hechos, transparencia y código bueno.
Gracias a la comunidad de r/argentina por el feedback que hizo posible esta v2.0.
Franco Luciano Carricondo
Diciembre 2025
