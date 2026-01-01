# AEE Protocol v2.1

**Motor de Certificación de Evidencia Digital con Seguridad Híbrida Post-Cuántica**

---

## Descripción

El Protocolo AEE (Aseguramiento de Evidencia Electrónica) es un sistema de certificación forense diseñado para garantizar la integridad, autenticidad y temporalidad de evidencia digital mediante criptografía híbrida clásica y post-cuántica.

### Características Principales

- **Criptografía Híbrida**: Ed25519 (clásica) + Kyber-768 (post-cuántica)
- **Quórum NTP Robusto**: Consenso temporal mediante múltiples servidores NTP
- **Serialización Canónica**: Garantiza reproducibilidad bit-a-bit (RFC 8785)
- **API REST**: FastAPI con documentación OpenAPI completa
- **Auditoría Inmutable**: Logs forenses de todas las operaciones

---

## Security Status

**Protocol logic successfully passed a simulated hostile audit (Jan 2026) covering Key Compromise, Source Code Access, Hash Collisions, and Implementation Bugs.**

See `audit/AUDIT_RESPONSES.md` for detailed responses to security scenarios.

**Status**: ✅ CLOSED - No critical findings identified

---

## Quick Start

### Ejecutar Tests Adversariales

Para validar que el protocolo rechaza correctamente intentos de manipulación:

```bash
# Desde el directorio raíz del proyecto
python aee/tests/test_adversarial.py
```

O si estás dentro del directorio `aee/`:

```bash
python tests/test_adversarial.py
```

Los tests validan:
- ✅ Detección de contenido alterado
- ✅ Rechazo de firmas con claves incorrectas
- ✅ Funcionamiento correcto del flujo normal

---

## Instalación

### Requisitos

- Python 3.8+
- Dependencias (ver `requirements.txt`)

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

---

## Uso Básico

### Certificación de Archivo

```python
from aee.pqc_hybrid import HybridCryptoEngine, generar_certificado_hibrido
from pathlib import Path

# Generar par de claves
engine = HybridCryptoEngine()
keypair = engine.generar_par_claves_hibrido()

# Certificar archivo
archivo = Path("evidencia.pdf")
certificado = generar_certificado_hibrido(archivo, keypair)

# Guardar certificado
import json
with open("certificado.json", "w") as f:
    json.dump(certificado, f, indent=2)
```

### Verificación de Certificado

```python
from aee.pqc_hybrid import verificar_certificado_hibrido

resultado = verificar_certificado_hibrido(archivo, certificado)
if resultado['exitoso']:
    print("✅ Certificado válido")
else:
    print(f"❌ Certificado inválido: {resultado['mensaje']}")
```

### API REST

```bash
# Iniciar servidor
uvicorn aee.api.fastapi_server:app --host 0.0.0.0 --port 8000

# Certificar (requiere API key)
curl -X POST "http://localhost:8000/api/v1/certify" \
  -H "X-API-Key: aee-dev-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "evidencia.pdf",
    "file_hash": "abc123...",
    "file_size_bytes": 1024
  }'
```

---

## Arquitectura

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

## Modelo de Seguridad v2.1

El Protocolo AEE v2.1 implementa las siguientes garantías de seguridad:

1. **Integridad**: Hash SHA-256 del archivo certificado
2. **Autenticidad**: Firma digital Ed25519 verificable públicamente
3. **Resistencia Post-Cuántica**: Sello Kyber-768 para protección futura
4. **Temporalidad**: Timestamp consensuado mediante quórum NTP
5. **No-repudio**: Firma criptográfica vinculada a clave privada

**Principio de Diseño**: Cumplimiento estricto del Principio de Kerckhoffs - la seguridad no depende de ocultar el código, sino de proteger las claves privadas.

---

## Documentación

- `audit/AUDIT_RESPONSES.md` - Respuestas formales a escenarios de ataque
- `docs/` - Documentación técnica adicional
- API Documentation: `http://localhost:8000/docs` (cuando el servidor está corriendo)

---

## Licencia

AGPLv3

---

## Autor

Desarrollo AEE  
Versión: 2.1.0  
Fecha: Enero 2026

