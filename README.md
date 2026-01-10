# AEE Protocol v1.2 - Deterministic Data Integrity

Sistema para preservación de integridad digital mediante hashing criptográfico determinista.

## How it Works

El protocolo combina contenido del archivo con metadata crítica (timestamp, autor, dispositivo) en formato JSON ordenado, generando un hash SHA-256 único:

```
File Content + Metadata (JSON) → SHA-256 Hash
```

Esto garantiza que cualquier cambio en contenido o metadata invalide el hash, detectando alteraciones.

## CLI Usage

Uso independiente desde terminal, sin necesidad de Telegram.

### Calcular Hash
```bash
python aee.py --hash <archivo>
```
Ejemplo:
```
$ python aee.py --hash manifiesto_aee.txt
SHA-256: 1635e079a84e2bed64c0e92bad279caf2611b886dd20484b7aa2964a14ad0193
Archivo: manifiesto_aee.txt
Tamaño: 106 bytes
```

### Verificar Integridad
```bash
python aee.py --verify <archivo> <hash>
```
Ejemplo (verificación positiva):
```
$ python aee.py --verify manifiesto_aee.txt 1635e079a84e2bed64c0e92bad279caf2611b886dd20484b7aa2964a14ad0193
✓ Integridad confirmada
```

Ejemplo (verificación negativa):
```
$ python aee.py --verify manifiesto_aee.txt 1635e079a84e2bed64c0e92bad279caf2611b886dd20484b7aa2964a14ad0193
✗ Integridad violada
```

## Determinismo y Reproducibilidad

El protocolo asegura que el mismo archivo y metadata generen el mismo hash SHA-256 en Windows, Linux y macOS, independientemente de la versión de Python. Esto se logra mediante:

- Serialización JSON normalizada (sort_keys=True, ensure_ascii=False, separators=(',', ':')).
- Concatenación binaria determinista: metadata_bytes + b'\x00' + file_bytes.
- Lectura de archivos en modo binario puro ('rb').

## Auditoría (--debug)

El CLI incluye flag --debug para auditoría externa:

```bash
python aee.py --hash <archivo> --debug
```

Output incluye:
- Representación hex de metadata_bytes.
- Longitud de metadata_bytes y file_bytes.
- Hex completo de bytes combinados.

Esto permite reproducción manual del hash por terceros sin acceso al código fuente.

## No-Garantías

El protocolo NO garantiza:
- Autenticidad o autoría del contenido.
- Identidad legal del usuario o dispositivo.
- Cadena de custodia completa (solo integridad del registro inicial).
- Veracidad o legalidad del contenido preservado.
- Protección contra manipulación de metadata externa.

Solo garantiza integridad criptográfica verificable del archivo + metadata en el momento de preservación.

## Changelog v1.2

- Hardening para determinismo reproducible cross-platform.
- Serialización JSON normalizada y concatenación binaria con delimitador.
- Flag --debug para auditoría externa.
- Alcance y garantías sin cambios.

## Instalación

```bash
pip install -r requirements.txt
```

## Licencia

MIT License © 2026 Protocolo AEE
