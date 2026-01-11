# Protocolo AEE (v1.2.0)
### Deterministic Integrity Anchor for Critical Data & AI Pipelines

El Protocolo AEE es un **primitive criptográfico** diseñado para crear anclajes de integridad deterministas. Vincula contenido binario con metadatos contextuales mediante una ejecución reproducible y verificable.

> **Filosofía de Diseño:** En sistemas dominados por procesos probabilísticos (IA), la integridad del dato de entrada debe ser determinista. AEE actúa como una aduana de integridad previa al procesamiento.

---

## 🏗️ Arquitectura Técnica

AEE es una **capa base de preservación**, no un sistema legal ni un framework de identidad.

- **Núcleo:** SHA-256 con concatenación binaria (`0x00`) y serialización canónica.
- **Cross-Platform:** Resultados idénticos en Windows, Linux y macOS.
- **Auditabilidad:** Verificación manual y reproducible (`--debug`).

📜 [Architecture Overview](./ARCHITECTURE.md)  
🛡️ [Threat Model](./THREAT_MODEL.md)

---

## 🚀 Uso

```bash
python aee.py --hash archivo.txt --user "ID-001" --debug

⚠️ Límites (Disclaimer)

No garantiza autoría legal (requiere PKI / firma digital externa).

No es resistente a computación cuántica (usa SHA-256 estándar).

Certifica integridad (el dato no cambió), no veracidad del contenido.

---

## Examples: Composing AEE with External Systems

AEE puede componerse con sistemas externos para capacidades adicionales. Estos ejemplos son composiciones externas, no parte del core AEE.

### Example: Digital Signature (PKI)
```python
# 1. Generate deterministic integrity anchor
anchor = aee.generate_anchor("document.pdf", metadata)

# 2. Sign anchor with external private key (PKI)
signature = private_key.sign(anchor.encode())

# 3. Verify signature with public key
public_key.verify(signature, anchor.encode())
```

### Example: Trusted Timestamp (TSA / RFC 3161)
```python
# 1. Generate anchor
anchor = aee.generate_anchor("dataset.parquet", metadata)

# 2. Send anchor to external TSA
timestamp_token = tsa_client.timestamp(anchor)
```

**Nota**: AEE NO implementa PKI ni TSA. Estas capacidades son responsabilidad de capas externas.
