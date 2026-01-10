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
