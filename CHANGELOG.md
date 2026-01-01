# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.1.0] - 2026-01-01

### Added
- **Audit Responses Documentation**: Documentación formal de respuestas a auditoría hostil simulada
  - Archivo `audit/AUDIT_RESPONSES.md` con 16 escenarios de ataque evaluados
  - Estado: CLOSED - No critical findings identified
  - Cobertura: Key Compromise, Source Code Access, Hash Collisions, Implementation Bugs

- **Adversarial Testing Suite**: Suite completa de tests de seguridad
  - `tests/test_adversarial.py` con 3 tests básicos:
    - Test 1: Verificación con contenido alterado (debe fallar)
    - Test 2: Verificación con clave pública incorrecta (debe fallar)
    - Test 3: Verificación exitosa de flujo normal

- **Security Model v2.1**: Refactorización de código con modelo de seguridad mejorado
  - Eliminación de degradación silenciosa en funciones críticas
  - Validación estricta de parámetros con excepciones claras
  - Fail-fast en verificaciones de integridad
  - Docstrings actualizados explicando cumplimiento con modelo v2.1

### Changed
- **Core Security Functions**: Refactorización de funciones de firma y verificación
  - `pqc_hybrid.py`: `firmar_dual()` y `verificar_dual()` con validación estricta
  - `core.py`: `verificar_integridad_total()` con fail-fast mejorado
  - `notario_pqc.py`: `certificar_archivo()` con manejo de errores mejorado
  - `api/routes.py`: Endpoints con manejo de errores sin degradación silenciosa

- **Documentation**: README.md actualizado a v2.1
  - Sección "Security Status" añadida
  - Referencia a documentación de auditoría
  - Quick Start para tests adversariales

### Security
- **Protocol Logic Audit**: Implementación de lógica de seguridad audit-ready
- **Consolidación de respuestas de auditoría hostil**: Documentación formal de posiciones de seguridad
- **Suite de tests adversariales**: Validación de resistencia a manipulación

### Technical Details
- Todas las funciones críticas ahora lanzan excepciones claras en lugar de degradación silenciosa
- Validación de parámetros mejorada en todas las funciones de firma/verificación
- Fail-fast implementado en verificaciones de integridad
- Docstrings actualizados con referencias al Modelo de Seguridad v2.1

---

## [2.0.0] - 2025-XX-XX

### Added
- Versión inicial del Protocolo AEE
- Criptografía híbrida Ed25519 + Kyber-768
- API REST con FastAPI
- Sistema de quórum NTP robusto

---

[2.1.0]: https://github.com/aee-protocol/aee-protocol/releases/tag/v2.1.0
[2.0.0]: https://github.com/aee-protocol/aee-protocol/releases/tag/v2.0.0

