# AEE Protocol v1.1 - Deterministic Data Integrity

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

## Changelog v1.1

- **Motor de Hashing Real**: Implementación determinista con metadata (timestamp, user_id, device_id).
- **Eliminación de Boilerplate**: Código simplificado, eliminación de comentarios redundantes y validaciones excesivas.
- **Soporte CLI**: Script `aee.py` para ejecución UNIX-style, independiente de Telegram.
- **Optimización de Seguridad**: No hardcoded keys, uso de variables de entorno.

## Instalación

```bash
pip install -r requirements.txt
```

## Licencia

MIT License © 2026 Protocolo AEE
