# Protocolo AEE – Preservación Temprana de Evidencia Digital

Sistema técnico auxiliar para la preservación inmediata de evidencia digital mediante cálculo de hash SHA-256 y registro temporal.

**Versión actual:** 1.0.0 (Implementación mínima funcional – MVP)  
**Fecha:** 04 de enero de 2026

## Propósito

Permitir a cualquier persona preservar la integridad y la existencia temporal de un archivo digital en el momento en que detecta su **eventual relevancia probatoria**, previo a cualquier procedimiento formal, judicial o administrativo.

El sistema está orientado a la **preconstitución técnica de evidencia**, no a la determinación de su veracidad.

## Funcionalidad actual

- Recepción de archivos vía Telegram
- Cálculo de hash criptográfico SHA-256
- Registro persistente con timestamp UTC
- Emisión de comprobante técnico en formato PDF
- Verificación posterior de integridad mediante hash
- Registro histórico de preservaciones por usuario

## Límites explícitos

Este sistema **NO**:

- Certifica la veracidad, autenticidad o licitud del contenido
- Valida autoría, contexto ni intención
- Reemplaza pericia informática, forense o judicial
- Detecta manipulaciones previas a la preservación
- Constituye instrumento público, certificación notarial ni dictamen pericial

El Protocolo AEE es una herramienta técnica auxiliar que **no garantiza la admisibilidad probatoria** del contenido preservado, la cual queda sujeta a la normativa vigente y a la valoración de la autoridad competente.

Ver alcance completo en: [SPECIFICATION.md](SPECIFICATION.md)

## Instalación y uso

Consultar [SPECIFICATION.md](SPECIFICATION.md) para detalles técnicos, operativos y delimitación jurídica del sistema.

## Licencia

MIT License © 2026 Protocolo AEE

## Contacto

Utilizar la sección *Issues* del repositorio para reportes o feedback técnico.
