# 🛡️ Protocolo AEE v2.1-HARDENED
### *Estándar de Preservación y Autenticidad de Evidencia Digital*

El **Protocolo AEE** es una herramienta de grado forense diseñada para la captura y sellado criptográfico de activos digitales. Alineado con la **Ley 25.506 (Firma Digital Argentina)**, este motor garantiza que cualquier archivo capturado sea inalterable y verificable ante la justicia.

## 🚀 Pilares Tecnológicos
* **Integridad:** Hash SHA-256 de 256 bits para detección de alteraciones bit a bit.
* **Autenticidad:** Criptografía de curva elíptica **Ed25519** para firma digital de autor.
* **Temporalidad:** Consenso de tiempo global vía NTP (Quórum de servidores de Google, Microsoft y Cloudflare).
* **Cadena de Custodia:** Captura de metadatos de bajo nivel (Inodos, Device IDs, File Size).

## 🛠️ Cómo usarlo
1.  **Certificar:** Ejecuta `python ejemplo_forense.py` para generar un certificado sellado.
2.  **Verificar:** Ejecuta `python verificar_aee.py`. El sistema validará la firma y el contenido automáticamente.

## ⚖️ Validez Legal
Este protocolo implementa mecanismos de **No-Repudio**, fundamentales para transformar un simple indicio digital en una evidencia con valor probatorio superior.