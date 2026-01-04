# Especificación Técnica – Protocolo AEE

**Versión:** 1.0.0  
**Fecha:** 04 de enero de 2026

## 1. Alcance Técnico

El Protocolo AEE (Acta de Evidencia Electrónica) es un sistema técnico auxiliar que permite la preservación inmediata de evidencia digital mediante:

- **Cálculo criptográfico de integridad:** Algoritmo SHA-256 (NIST FIPS 180-4)
- **Registro temporal:** Timestamp UTC según RFC 3339
- **Persistencia:** Base de datos SQLite con estructura normalizada
- **Comprobante técnico:** Documento PDF con metadatos y hash

### 1.1 Funcionalidades Técnicas

- Recepción de archivos digitales (imágenes, documentos) vía Telegram Bot
- Cálculo automático de hash SHA-256 del contenido binario
- Almacenamiento persistente con identificación única
- Generación de certificado PDF con información técnica
- Verificación posterior de integridad mediante comparación de hash
- Consulta de historial de preservaciones por usuario

## 2. Separación Técnica vs. Jurídica

### 2.1 Lo que el Sistema Certifica (Alcance Técnico)

El Protocolo AEE certifica únicamente:

1. **Integridad del binario:** El hash SHA-256 del archivo preservado
2. **Existencia temporal:** El timestamp UTC del momento de preservación
3. **Identidad del usuario:** El ID de Telegram que realizó la preservación
4. **Metadatos del archivo:** Nombre, tamaño, tipo MIME (cuando disponibles)

### 2.2 Lo que el Sistema NO Certifica

El Protocolo AEE **NO** certifica:

- **Veracidad del contenido:** La exactitud, verdad o autenticidad de la información contenida
- **Autoría:** Quién creó o generó el archivo original
- **Contexto:** Las circunstancias, intenciones o implicaciones del contenido
- **Legalidad:** La conformidad con normativa vigente
- **Manipulación previa:** Alteraciones que pudieran haber ocurrido antes de la preservación

## 3. Limitaciones Técnicas

### 3.1 Limitaciones del Hash Criptográfico

- El hash SHA-256 garantiza que el archivo no ha sido alterado **desde** la preservación, no antes
- No detecta manipulaciones que ocurrieron antes del registro en el sistema
- Dos archivos diferentes pueden tener el mismo hash solo teóricamente (resistencia a colisión: 2^256)

### 3.2 Limitaciones del Timestamp

- El timestamp refleja el momento de preservación, no necesariamente el momento de creación del archivo
- Depende de la sincronización del sistema operativo del servidor
- No incluye validación mediante NTP o autoridad certificadora de tiempo

### 3.3 Limitaciones del Almacenamiento

- La base de datos SQLite es local y no está replicada
- No existe respaldo automático fuera del servidor
- La persistencia depende de la integridad del sistema de archivos del servidor

### 3.4 Limitaciones del Canal de Entrada

- La recepción vía Telegram depende de la infraestructura de Telegram
- El bot no puede verificar la identidad real del usuario (solo el ID de Telegram)
- No existe validación de dos factores o autenticación adicional

## 4. Delimitación Jurídica

### 4.1 Disclaimers Legales (Argentina)

El Protocolo AEE es una **herramienta técnica auxiliar** que debe entenderse en los siguientes términos:

#### No es un Instrumento Público

El certificado emitido por el sistema **NO** constituye un instrumento público según la normativa argentina. No reemplaza actas notariales, certificaciones oficiales ni documentos públicos.

#### No es una Certificación Notarial

El sistema **NO** realiza certificación notarial. No implica intervención de escribano público ni validez notarial. El comprobante técnico es un documento generado automáticamente sin intervención humana que valide su contenido.

#### No Reemplaza Pericia Informática o Forense

El Protocolo AEE **NO** reemplaza:

- Pericia informática formal
- Análisis forense de evidencia digital
- Dictamen pericial judicial
- Evaluación técnica por profesionales especializados

#### Admisibilidad Probatoria

La **admisibilidad probatoria** del contenido preservado mediante este sistema queda sujeta a:

- La normativa procesal vigente (Código Procesal Civil y Comercial de la Nación, Código Procesal Penal, etc.)
- La valoración de la autoridad judicial competente
- Los requisitos específicos de cada procedimiento
- La evaluación caso por caso según las circunstancias

**El Protocolo AEE no garantiza la admisibilidad ni la valoración probatoria** del material preservado.

### 4.2 Uso Recomendado

Este sistema está orientado a la **preconstitución técnica de evidencia**, permitiendo:

- Preservación inmediata cuando se detecta eventual relevancia probatoria
- Registro técnico previo a procedimientos formales
- Documentación auxiliar para asesoramiento legal posterior
- Registro de integridad como complemento de otros métodos de preservación

**Se recomienda consultar con asesores legales** sobre la estrategia probatoria adecuada para cada caso.

## 5. Arquitectura Técnica

### 5.1 Componentes

- **Bot de Telegram:** Interfaz de usuario para recepción de archivos
- **Motor de Hash:** Cálculo SHA-256 del contenido binario
- **Base de Datos:** SQLite con tabla `preservations`
- **Generador de PDF:** Creación de certificado técnico con ReportLab
- **API de Verificación:** (Reservado para implementación futura)

### 5.2 Esquema de Base de Datos

```sql
CREATE TABLE preservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    file_size INTEGER NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    timestamp_utc DATETIME NOT NULL,
    _signature TEXT NULL
);

CREATE INDEX ix_preservations_file_hash ON preservations(file_hash);
CREATE INDEX ix_preservations_user_id ON preservations(user_id);
```

### 5.3 Formato del Certificado PDF

El certificado incluye:

- Encabezado identificatorio
- ID de preservación
- Timestamp UTC
- Hash SHA-256 completo
- Metadatos del archivo
- Disclaimers legales
- Especificaciones técnicas del algoritmo

## 6. Referencias Técnicas

- **SHA-256:** NIST FIPS 180-4, RFC 6234
- **Timestamp:** RFC 3339 (ISO 8601)
- **SQLite:** Versión 3.x
- **Telegram Bot API:** python-telegram-bot 20.7+

## 7. Mantenimiento y Evolución

Esta especificación corresponde a la versión 1.0.0 (MVP). Futuras versiones pueden incluir:

- Integración de firma digital
- Validación mediante NTP
- Replicación de base de datos
- API REST para verificación externa

Los cambios en la especificación se documentarán en este archivo con versionado semántico.

---

**Documento técnico-jurídico**  
Protocolo AEE v1.0.0  
04 de enero de 2026
