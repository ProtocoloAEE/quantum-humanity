# Changelog

Todas las modificaciones notables a este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-12-28

### Añadido
- **Blindaje legal completo** para cumplimiento Ley 25.506
- **Sellado temporal NTP multi-servidor** (Google, NIST, Microsoft, AFIP)
- **Motor de riesgo con fundamentación jurídica automática**
  - Mapeo a Ley 26.831 (Mercado de Capitales)
  - Mapeo a Ley 24.240 (Defensa del Consumidor)  
  - Mapeo a Código Penal Arts. 172, 173, 310
- **Generador de informes para abogados** (`report_generator.py`)
- **Estructura de acta probatoria** en certificados JSON
- **Guía de uso jurídico** completa (`USO_JURIDICO.md`)
- **Política de seguridad** formal (`SECURITY.md`)
- **Guía de contribución** (`CONTRIBUTING.md`)
- **Plantillas para demandas** en documentación
- **Soporte para verificación independiente** de certificados

### Cambiado
- **README completamente rediseñado** con foco profesional
- **Certificados JSON reformateados** como "Actas de Observación Técnica"
- **Mejorada validación de entrada** para evitar errores de usuario
- **Refactorizado código de hash** para mejor mantenibilidad
- **Actualizadas todas las dependencias** a últimas versiones estables

### Mejoras de Seguridad
- **Protección contra replays** en sellos temporales
- **Validación estricta de JSON** para prevenir inyección
- **Sanitización de URLs** de entrada
- **Manejo seguro de datos personales** en logs

### Compatibilidad Legal
- ✅ **Ley 25.506** - Firma Digital (Arts. 3, 7, 8)
- ✅ **Ley 26.831** - Mercado de Capitales
- ✅ **Ley 24.240** - Defensa del Consumidor
- ✅ **Código Penal** - Arts. 172, 173, 310
- ✅ **Ley 25.326** - Protección de Datos Personales
- ✅ **RFC 3161** - Time-Stamp Protocol (compatible)
- ✅ **NIST FIPS 202** - SHA-3 Standard

## [1.3.0] - 2025-12-20

### Añadido
- Primer release pública del protocolo
- Sistema de certificación básica con SHA3-512
- Modo interactivo para creación de evidencia
- Generación de certificados JSON
- Sellos de integridad soberanos
- Evaluación de riesgo automatizada
- Watermarking resistente a reescritura por IA
- Detección determinística de manipulación

### Características Iniciales
- Vinculación a identidad (DNI)
- Timestamps UTC precisos
- Hash layering (3 capas)
- Verificación rápida con prefijos
- Exportación a múltiples formatos
- Documentación básica en español

## [1.0.0] - 2025-11-15

### Lanzamiento Interno
- Concepto inicial del Protocolo AEE
- Pruebas de concepto con criptografía post-cuántica
- Primeros experimentos con watermarking vs IA
- Desarrollo de arquitectura básica
- Definición de estándares de evidencia digital

---

## Convención de Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/):
- **MAYOR** (1.x.x): Cambios incompatibles con versiones anteriores
- **MENOR** (x.1.x): Nuevas funcionalidades compatibles
- **PATCH** (x.x.1): Correcciones de bugs compatibles

## Registro de Cambios Técnicos

Para cambios técnicos detallados, ver:
- Commits en GitHub: `git log --oneline`
- Issues cerrados: GitHub Projects
- Pull requests: `https://github.com/quantum-humanity/aee-protocol/pulls`

---

*Este CHANGELOG es mantenido por Franco Carricondo (DNI 35.664.619).  
Para sugerencias o correcciones, abrir issue en GitHub.*
