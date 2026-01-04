# Especificación Técnica – Protocolo AEE

**Versión:** 1.0.0  
**Fecha:** 04 de enero de 2026

---

## 1. Alcance Técnico

El Protocolo AEE (Acta de Evidencia Electrónica) es un sistema técnico auxiliar destinado a la **preservación inmediata de evidencia digital**, mediante mecanismos criptográficos y de registro temporal.

El sistema permite registrar la **integridad** y la **existencia temporal** de un archivo digital en un momento determinado, sin efectuar valoración sobre su contenido.

Los componentes técnicos principales son:

- **Cálculo criptográfico de integridad:** Algoritmo SHA-256 (NIST FIPS 180-4)
- **Registro temporal:** Timestamp UTC en formato RFC 3339
- **Persistencia:** Base de datos SQLite con estructura normalizada
- **Comprobante técnico:** Documento PDF generado automáticamente con metadatos y hash

---

## 1.1 Funcionalidades Técnicas

El sistema implementa las siguientes funcionalidades:

- Recepción de archivos digitales (imágenes, documentos, etc.) mediante un bot de Telegram
- Cálculo automático del hash SHA-256 sobre el contenido binario recibido
- Almacenamiento persistente del registro técnico con identificación única
- Generación de un certificado PDF con información técnica asociada
- Verificación posterior de integridad mediante comparación de hash
- Consulta de historial de preservaciones por usuario

---

## 2. Separación entre Alcance Técnico y Consideraciones Externas

El diseño del Protocolo AEE se basa en una separación estricta entre lo que el sistema **registra técnicamente** y cualquier interpretación externa de dichos registros.

---

## 2.1 Lo que el Sistema Registra (Alcance Técnico)

El Protocolo AEE registra exclusivamente:

1. **Integridad del archivo:** Hash SHA-256 del contenido binario preservado
2. **Existencia temporal:** Timestamp UTC del momento de preservación
3. **Identificación del usuario:** ID de Telegram que realizó la operación
4. **Metadatos técnicos:** Nombre del archivo, tamaño y tipo MIME (cuando están disponibles)

Estos registros son generados de forma automática por el sistema.

---

## 2.2 Lo que el Sistema NO Registra ni Determina

El Protocolo AEE **no determina ni valida**:

- La veracidad, exactitud o autenticidad del contenido del archivo
- La autoría o procedencia del material
- El contexto en el que fue creado o utilizado
- La legalidad del contenido
- La existencia o no de manipulaciones previas a la preservación
- La intención de las partes involucradas

---

## 3. Limitaciones Técnicas

---

### 3.1 Limitaciones del Hash Criptográfico

- El hash SHA-256 permite verificar que el archivo **no fue modificado desde el momento de la preservación**
- No permite detectar alteraciones ocurridas antes de dicho registro
- La resistencia a colisiones se basa en las propiedades criptográficas conocidas del algoritmo (2^256)

---

### 3.2 Limitaciones del Registro Temporal

- El timestamp refleja el momento de recepción del archivo por el sistema
- No representa necesariamente el momento de creación del archivo
- Depende de la sincronización del sistema operativo del servidor
- No incluye, en esta versión, validación por autoridad externa de tiempo

---

### 3.3 Limitaciones del Almacenamiento

- La base de datos SQLite es local al entorno de ejecución
- No existe replicación automática ni respaldo externo garantizado
- La persistencia depende de la integridad del sistema de archivos del servidor

---

### 3.4 Limitaciones del Canal de Entrada

- La recepción de archivos depende de la infraestructura de Telegram
- El sistema no verifica la identidad real del usuario, solo el identificador asignado por la plataforma
- No se implementan mecanismos de autenticación adicionales en esta versión

---

## 4. Alcance y Límites del Sistema

---

### 4.1 Declaración de Alcance No Legal

⚠️ **IMPORTANTE**

Este documento describe exclusivamente el **funcionamiento técnico** del Protocolo AEE.

No constituye asesoramiento legal, pericial ni jurídico.  
La interpretación, utilización y valoración de los registros generados por el sistema corresponden exclusivamente a los profesionales y autoridades competentes que intervengan en cada caso.

---

### 4.2 Naturaleza del Comprobante Generado

El certificado emitido por el sistema es un **documento técnico automatizado**, generado sin intervención humana.

No reemplaza ni equivale a:

- Instrumentos públicos
- Certificaciones notariales
- Actas oficiales
- Dictámenes periciales
- Informes forenses profesionales

---

### 4.3 Relación con Procedimientos Formales

El Protocolo AEE no sustituye procedimientos formales de preservación, análisis o evaluación de evidencia digital.

Su finalidad es permitir una **preservación técnica temprana**, que puede servir como complemento de otros métodos o actuaciones posteriores, según el criterio de los profesionales intervinientes.

El sistema **no garantiza** la admisibilidad ni la valoración probatoria de los registros generados.

---

### 4.4 Uso Recomendado

El sistema está orientado a:

- Preservar evidencia digital en el momento en que se detecta una posible relevancia futura
- Documentar técnicamente la integridad de un archivo
- Facilitar verificaciones posteriores de no alteración
- Complementar asesoramiento legal o técnico posterior

Se recomienda consultar con profesionales especializados antes de utilizar los registros en contextos formales.

---

## 5. Arquitectura Técnica

---

### 5.1 Componentes Principales

- **Bot de Telegram:** Interfaz de entrada de archivos
- **Motor de Hash:** Cálculo SHA-256 del contenido binario
- **Base de Datos:** SQLite con tabla de preservaciones
- **Generador de PDF:** Emisión de certificado técnico
- **Módulo de Verificación:** Comparación de hash para validación posterior

---

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
5.3 Contenido del Certificado PDF
El certificado incluye, como mínimo:

Identificación del sistema

ID de preservación

Timestamp UTC

Hash SHA-256 completo

Metadatos técnicos del archivo

Descripción técnica del alcance del registro

6. Referencias Técnicas
SHA-256: NIST FIPS 180-4

Timestamp: RFC 3339 / ISO 8601

SQLite: versión 3.x

Telegram Bot API (python-telegram-bot 20.7+)

7. Mantenimiento y Evolución
Este documento corresponde a la versión 1.0.0 (MVP) del Protocolo AEE.

Las versiones futuras podrán incorporar, entre otros:

Integración de firma digital

Mejora en validación temporal

Replicación de almacenamiento

Interfaces externas de verificación

Las modificaciones se documentarán mediante versionado semántico.

Documento técnico descriptivo del sistema
Protocolo AEE – Versión 1.0.0
04 de enero de 2026