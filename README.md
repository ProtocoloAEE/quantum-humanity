# Protocolo AEE (v1.2.1)
### Deterministic Integrity Anchor for Critical Data & AI Pipelines

Protocolo de Soberanía Digital y Anclaje Determinista de Integridad.

> **Filosofía de Diseño:** En sistemas dominados por procesos probabilísticos (IA), la integridad del dato de entrada debe ser determinista. AEE actúa como una aduana de integridad previa al procesamiento.

---

## 🎯 El Problema Que Resuelve

En pipelines de IA y datos críticos, el riesgo no es solo que los modelos fallen—es que **no tenés forma de verificar que los datos que procesaste son los que declaras**.

AEE resuelve esto de forma simple:

1. **Genera un anclaje determinista** (hash SHA-256) del archivo/dataset
2. **Almacena ese anclaje** en tu sistema de auditoría
3. **Verifica después** que el archivo no fue modificado

### Casos de Uso

✅ **Auditoría de datasets** antes de entrenar modelos de IA  
✅ **Control de integridad** en pipelines críticos sin exponerlos a la nube  
✅ **Compliance regulatorio**: demostrar que los datos procesados son los que declaras  
✅ **Forensia digital**: detectar cuándo un archivo fue modificado  
✅ **Verificación previa a decisiones** humanas o regulatorias

---

## 🏗️ Arquitectura Técnica

AEE es una **capa base de preservación**, no un sistema legal ni un framework de identidad.

- **Núcleo:** SHA-256 con serialización canónica
- **Cross-Platform:** Resultados idénticos en Windows, Linux y macOS
- **Auditabilidad:** Verificación manual y reproducible
- **Sin dependencias externas:** Solo Python estándar

Para detalles técnicos de la implementación, revisa `aee/protocol.py` que contiene docstrings completos.

---

## 🚀 Uso Rápido

### Generar un Anclaje de Integridad

```bash
python main.py --hash dataset.csv --user "audit-test"
```

Output:
```
════════════════════════════════════════════
AEE - Integrity Audit Test
════════════════════════════════════════════
File  : dataset.csv
User  : audit-test

✔ INTEGRITY ANCHOR GENERATED
════════════════════════════════════════════
Anchor: 13ac0b6d7c175349477a9ae65a0ab348be712c01a7c46e8ba2489e60b7332bbc
Status: GENERATED
════════════════════════════════════════════
```

### Verificar Integridad Posterior

Después de procesar el archivo, verifica que no fue modificado:

```bash
python main.py --verify dataset.csv --anchor 13ac0b6d7c175349477a9ae65a0ab348be712c01a7c46e8ba2489e60b7332bbc
```

Output si el archivo está intacto:
```
════════════════════════════════════════════
AEE - Integrity Verification
════════════════════════════════════════════
✔ Status: VERIFIED

Expected Anchor: 13ac0b6d7c175349477a9ae65a0ab348be712c01a7c46e8ba2489e60b7332bbc
Current Anchor : 13ac0b6d7c175349477a9ae65a0ab348be712c01a7c46e8ba2489e60b7332bbc

Timestamp: 2026-01-15T03:16:50.670939Z
════════════════════════════════════════════
```

Output si fue modificado:
```
════════════════════════════════════════════
AEE - Integrity Verification
════════════════════════════════════════════
✖ Status: MISMATCH

Expected Anchor: 13ac0b6d7c175349477a9ae65a0ab348be712c01a7c46e8ba2489e60b7332bbc
Current Anchor : c9c81b9162dc76edcdc4f81a856e8258fdf463f62bacf0a3f25fdf6b995f28ba

Timestamp: 2026-01-15T03:15:47.872629Z
════════════════════════════════════════════
```

---

## 📦 Integración en Python

Si querés usar AEE como módulo dentro de tu aplicación:

```python
from aee import AEEProtocol

# Instanciar protocolo
aee = AEEProtocol()

# 1. Generate anchor on dataset arrival
anchor_result = aee.generate("dataset.parquet", user="audit-system")
print(f"Anchor: {anchor_result['anchor']}")

# 2. Store anchor in audit log (your persistence layer)
store_in_audit_log(
    dataset_id="ds_12345",
    anchor=anchor_result['anchor'],
    metadata=anchor_result['metadata']
)

# 3. Before processing, verify integrity
verification = aee.verify("dataset.parquet", anchor_result['anchor'])

if not verification['verified']:
    raise IntegrityException(
        f"Dataset integrity compromised. "
        f"Expected: {verification['expected_anchor']}, "
        f"Got: {verification['current_anchor']}"
    )

# Safe to process
process_dataset("dataset.parquet")
```

### Batch Processing

Para múltiples archivos:

```python
from aee import AEEProtocol

aee = AEEProtocol()

files = ["data1.csv", "data2.csv", "data3.csv"]
anchors = aee.batch_generate(files, user="batch-audit")

for result in anchors:
    if "error" not in result:
        print(f"{result['metadata']['filename']}: {result['anchor']}")
    else:
        print(f"Failed: {result['error']}")
```

---

## ✅ Lo Que AEE Garantiza

| Garantía | Descripción |
|----------|-------------|
| ✅ **Integridad Bitwise** | El archivo no fue modificado (ni un byte) |
| ✅ **Determinismo** | Mismo archivo = mismo hash, siempre |
| ✅ **Cross-Platform** | Windows, Linux, macOS generan el mismo resultado |
| ✅ **Verificable** | Puedes verificar sin software adicional (solo Python) |
| ✅ **Auditabilidad** | Trazabilidad completa: usuario, timestamp, metadata |

---

## ❌ Lo Que AEE NO Garantiza

| Limitación | Solución |
|-----------|----------|
| ❌ **Autoría legal** | Requiere PKI externa (integra con OpenSSL, libraries de firma digital) |
| ❌ **Cifrado** | AEE no oculta el contenido, solo verifica integridad |
| ❌ **Resistencia a computación cuántica** | Usa SHA-256 estándar. Para QKD, integra NIST Post-Quantum standards |
| ❌ **Firma legal** | Sin PKI, el hash no es prueba legal. Integra con TSA (RFC 3161) |
| ❌ **Seguridad contra atacante con acceso físico** | Si alguien modifica archivo Y hash, necesitás verificación externa |

---

## 🔗 Composición con Sistemas Externos

AEE puede componerse con sistemas externos para capacidades adicionales. Estos ejemplos son composiciones externas, no parte del core AEE.

### Ejemplo: Firma Digital (PKI)

Para que la auditoría sea **legal y no repudiable**:

```python
from aee import AEEProtocol
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

aee = AEEProtocol()

# 1. Generate deterministic integrity anchor
anchor = aee.generate("document.pdf", user="legal-audit")

# 2. Sign anchor with PKI (external)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
signature = private_key.sign(
    anchor['anchor'].encode(),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# 3. Store both anchor and signature
store_legal_audit(
    anchor=anchor['anchor'],
    signature=signature,
    public_key=private_key.public_key()
)

# 4. Verify with public key later
public_key.verify(signature, anchor['anchor'].encode(), ...)
```

**Nota:** AEE NO implementa PKI. Estas capacidades son responsabilidad de capas externas.

### Ejemplo: Trusted Timestamp (TSA / RFC 3161)

Para **prueba temporal irrefutable**:

```python
aee = AEEProtocol()
anchor = aee.generate("dataset.parquet", user="audit-system")

# Send anchor to external TSA (RFC 3161 compliant)
tsa_response = tsa_client.timestamp(
    data=anchor['anchor'].encode(),
    tsa_url="http://timestamp.server.com"
)

# Store anchor + TSA token
store_audit_with_timestamp(
    anchor=anchor['anchor'],
    tsa_token=tsa_response.get_token()
)
```

**Nota:** AEE NO implementa TSA. Integra con servicios como Sectigo, Digicert, o servidores RFC 3161 internos.

---

## 🧪 Testing

### Test Manual

```bash
cd examples/audit-dataset
.\run_test.ps1  # Windows PowerShell
bash run_test.sh  # Linux/macOS
```

Expected output:
```
AEE - Integrity Audit Test
---
✔ INTEGRITY ANCHOR GENERATED
✔ Status: VERIFIED
Test Results: PASSED
```

---

## ⚠️ Disclaimers

- No garantiza autoría legal (requiere PKI / firma digital externa)
- No es resistente a computación cuántica (usa SHA-256 estándar)
- Certifica integridad (el dato no cambió), no veracidad del contenido
- No cifra el archivo (usa hash determinista, no encriptación)
- Requiere almacenamiento seguro del anchor (usar base de datos con auditoría)

---

## 📚 Documentación

Para detalles técnicos de la implementación, revisa:
- `aee/protocol.py` — Código completo con docstrings
- `main.py` — CLI con argumentos y manejo de errores
- `examples/audit-dataset/` — Ejemplo reproducible

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

Para reportar bugs o sugerir features:
1. Abre un issue con evidencia técnica
2. Proporciona dataset reproducible
3. Documenta el comportamiento esperado vs actual

---

## 📧 Contact

Protocol Architect: Franco Carricondo  
GitHub: https://github.com/ProtocoloAEE/quantum-humanity  
Version: 1.2.1  
Last Updated: January 15, 2026