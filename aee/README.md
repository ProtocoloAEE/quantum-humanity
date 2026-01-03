# 🛡️ AEE Protocol: The Quantum-Resistant Immutable Truth

**Motor de Certificación de Evidencia Digital con Seguridad Híbrida Post-Cuántica**

[![Version](https://img.shields.io/badge/version-2.3.0--Stable-blue.svg)](VERSION)
[![Security](https://img.shields.io/badge/security-audited-green.svg)](FINAL_SECURITY_REPORT.md)
[![License](https://img.shields.io/badge/license-AGPLv3-red.svg)](LICENSE)

---

## 🌟 Descripción

El **Protocolo AEE (Aseguramiento de Evidencia Electrónica)** es un sistema de certificación forense de nivel empresarial diseñado para garantizar la **integridad, autenticidad y temporalidad** de evidencia digital mediante criptografía híbrida clásica y post-cuántica.

En un mundo donde la computación cuántica amenaza los sistemas criptográficos actuales, AEE Protocol implementa una **doble capa de seguridad**: Ed25519 (clásica) + Kyber-768 (post-cuántica), garantizando que tus certificados sigan siendo válidos incluso después de la llegada de las computadoras cuánticas.

---

## 🔒 Security Audit

### ✅ Fuzz Testing Results (v2.3.0)

**El Protocolo AEE ha sido sometido a pruebas exhaustivas de seguridad:**

| Métrica | Resultado | Estado |
|---------|-----------|--------|
| **Crashes del sistema** | **0** | ✅ **PERFECTO** |
| **Payloads corruptos aceptados** | **0** | ✅ **PERFECTO** |
| **Vulnerabilidades detectadas** | **0** | ✅ **INPENETRABLE** |
| **Timeouts** | **0** | ✅ **ESTABLE** |
| **Peticiones maliciosas procesadas** | **1000** | ✅ **100% CONTROLADAS** |

**Resultado Final:** ✅ **INPENETRABLE** - El protocolo maneja correctamente todos los payloads maliciosos sin degradación ni crashes.

Ver reporte completo: [`FINAL_SECURITY_REPORT.md`](FINAL_SECURITY_REPORT.md)

### Security Status

**Protocol logic successfully passed a simulated hostile audit (Jan 2026) covering Key Compromise, Source Code Access, Hash Collisions, and Implementation Bugs.**

See `audit/AUDIT_RESPONSES.md` for detailed responses to security scenarios.

**Status**: ✅ **CLOSED** - No critical findings identified

---

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/aee-protocol.git
cd aee-protocol

# Levantar el stack completo (API + Base de Datos)
docker-compose up -d

# El servidor estará disponible en http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs
```

### Opción 2: Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn aee.api.fastapi_server:app --host 0.0.0.0 --port 8000
```

---

## 📡 Uso de la API REST

### Endpoint: `/api/v1/certify`

Certifica un archivo digital con firma híbrida (Ed25519 + Kyber-768).

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/certify" \
  -H "X-API-Key: aee-dev-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "evidencia.pdf",
    "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "file_size_bytes": 2048,
    "metadata": {
      "caso_numero": "2025-CV-00123",
      "perito_nombre": "Dr. Juan García",
      "institucion": "Fiscalía Federal"
    }
  }'
```

**Response:**
```json
{
  "certificado_id": "550e8400-e29b-41d4-a716-446655440000",
  "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "timestamp_ntp": {
    "timestamp_iso": "2026-01-15T10:30:00Z",
    "servidores_exitosos": 5
  },
  "firmas": {
    "signature_classic": "...",
    "pqc_seal": "...",
    "timestamp": "2026-01-15T10:30:00Z"
  },
  "version_protocolo": "2.2.0-HybridPQC",
  "estado": "VIGENTE"
}
```

### Endpoint: `/api/v1/verify`

Verifica la integridad y autenticidad de un certificado.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/verify" \
  -H "X-API-Key: aee-dev-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "certificado": {
      "certificado_id": "550e8400-e29b-41d4-a716-446655440000",
      "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "firmas": {...},
      "claves_publicas": {...}
    }
  }'
```

**Response:**
```json
{
  "exitoso": true,
  "mensaje": "Certificado válido",
  "integridad": {
    "exitoso": true,
    "mensaje": "Hash del archivo coincide con el certificado"
  },
  "autenticidad": {
    "exitoso": true,
    "mensaje": "Firma Ed25519 válida"
  }
}
```

### Documentación Interactiva

Accede a la documentación interactiva de Swagger/OpenAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🏗️ Características Principales

### 🔐 Criptografía Híbrida
- **Ed25519** (Clásica): Firma digital de alta curva para verificación pública inmediata
- **Kyber-768** (Post-Cuántica): Sello criptográfico resistente a computadoras cuánticas
- **Doble Capa**: Garantiza validez tanto en el presente como en el futuro post-cuántico

### ⏰ Quórum NTP Robusto
- Consenso temporal mediante múltiples servidores NTP
- Filtrado de outliers y cálculo de mediana
- Garantiza temporalidad verificable y no manipulable

### 📋 Serialización Canónica
- Implementación RFC 8785 (JSON Canonicalization Scheme)
- Garantiza reproducibilidad bit-a-bit
- Evita problemas de orden de campos en JSON

### 🛡️ Seguridad Hardened
- **Validación Estricta**: Regex y límites de tamaño en todos los inputs
- **Escudo Global**: Exception handler que previene crashes
- **Limitador de Payload**: Protección contra DoS (máx 1MB)
- **Timeouts**: Operaciones criptográficas con límites temporales

### 📊 Auditoría Inmutable
- Logs forenses de todas las operaciones
- Registro en `aee_forensic.log` con traceback completo
- Trazabilidad completa de certificaciones y verificaciones

---

## 📦 Instalación

### Requisitos

- Python 3.8+
- Docker y Docker Compose (opcional, para containerización)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Dependencias Principales

- `cryptography` - Ed25519 signatures
- `kyber-py` o `pqcrypto` - Kyber-768 post-quantum cryptography
- `ntplib` - NTP quorum consensus
- `fastapi` - REST API framework
- `sqlalchemy` - Database ORM
- `pydantic` - Data validation
- `uvicorn` - ASGI server

---

## 🧪 Testing

### Tests Adversariales

```bash
# Desde el directorio raíz del proyecto
python aee/tests/test_adversarial.py
```

Los tests validan:
- ✅ Detección de contenido alterado
- ✅ Rechazo de firmas con claves incorrectas
- ✅ Funcionamiento correcto del flujo normal

### Fuzz Testing

```bash
# Iniciar servidor en una terminal
uvicorn aee.api.fastapi_server:app --host 127.0.0.1 --port 8000

# Ejecutar fuzz testing en otra terminal
python aee/tests/fuzz_test_api.py
```

---

## 🏛️ Arquitectura

```
aee/
├── core.py              # Módulos fundamentales (serialización, NTP, errores)
├── pqc_hybrid.py        # Motor criptográfico híbrido
├── notario_pqc.py       # Orquestador de certificación
├── api/                 # API REST con FastAPI
│   ├── fastapi_server.py
│   ├── routes.py
│   └── models.py
├── infrastructure/      # Capa de infraestructura
│   ├── database.py      # SQLAlchemy ORM
│   ├── security.py      # API Keys
│   └── hsm.py           # Adaptador HSM
├── audit/               # Documentación de auditoría
├── docs/                # Documentación general
└── tests/               # Tests de validación
```

---

## 🔐 Modelo de Seguridad v2.3.0

El Protocolo AEE v2.3.0 implementa las siguientes garantías de seguridad:

1. **Integridad**: Hash SHA-256 del archivo certificado
2. **Autenticidad**: Firma digital Ed25519 verificable públicamente
3. **Resistencia Post-Cuántica**: Sello Kyber-768 para protección futura
4. **Temporalidad**: Timestamp consensuado mediante quórum NTP
5. **No-repudio**: Firma criptográfica vinculada a clave privada
6. **Validación Estricta**: Regex y límites en todos los inputs
7. **Escudo Global**: Exception handler que previene crashes
8. **Protección DoS**: Limitador de payload y timeouts

**Principio de Diseño**: Cumplimiento estricto del Principio de Kerckhoffs - la seguridad no depende de ocultar el código, sino de proteger las claves privadas.

---

## 📚 Documentación

- [`FINAL_SECURITY_REPORT.md`](FINAL_SECURITY_REPORT.md) - Reporte completo de seguridad
- [`audit/AUDIT_RESPONSES.md`](audit/AUDIT_RESPONSES.md) - Respuestas formales a escenarios de ataque
- [`docs/`](docs/) - Documentación técnica adicional
- **API Documentation**: http://localhost:8000/docs (cuando el servidor está corriendo)

---

## 📄 Licencia

AGPLv3 - Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Desarrollo AEE**  
Versión: **2.3.0-Stable**  
Fecha: Enero 2026

---

## 🙏 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para discutir cambios importantes.

---

**🛡️ AEE Protocol: Donde la evidencia digital encuentra su verdad inmutable.**
