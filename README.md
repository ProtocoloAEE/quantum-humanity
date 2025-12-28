# 🔐 Protocolo AEE - Quantum Humanity v1.3

**Auditoría Ética y Evidencia Soberana**  
*Estándar global de certificación ciudadana post-cuántica*

---

## 🎯 ¿Qué es el Protocolo AEE?

El **Protocolo AEE (Auditoría Ética y Evidencia Soberana)** es un sistema de certificación digital que permite a cualquier ciudadano generar evidencia técnica con **validez legal**, utilizando criptografía determinista basada en identidad física y operación **100% offline**.

### Principios Fundamentales
1. **Soberanía real** - Ejecución en tu máquina, sin servidores
2. **Identidad verificable** - Vinculada a DNI/documento real
3. **Integridad criptográfica** - SHA3-512 post-cuántico
4. **Transparencia total** - Código abierto auditable
5. **Marco legal claro** - Cumple Ley 25.506 (Argentina)

---

## 🚀 Comenzar en 2 minutos

### Requisitos
- Python 3.8+
- Sistema operativo cualquiera (Windows, Linux, macOS)
- Conexión a Internet (solo para descarga inicial)

### Instalación
```bash
# 1. Clonar repositorio
git clone https://github.com/quantum-humanity/aee-protocol
cd aee-protocol

# 2. Verificar que funciona
python kyber_engine.py

# 3. Ejecutar certificador
python certificar_evidencia_aee.py
```

---

## 📋 Uso Básico

### Modo Interactivo (Recomendado para empezar)
```bash
python certificar_evidencia_aee.py
# Seleccionar opción 1 y seguir las instrucciones
```

### Modo Archivo (Para evidencia existente)
```bash
python certificar_evidencia_aee.py --modo archivo --archivo mi_evidencia.json
```

### Generar Ejemplo Demostrativo
```bash
python certificar_evidencia_aee.py --modo ejemplo
```

---

## 🏛️ Marco Legal (Argentina)

### Base Jurídica
- **Ley 25.506** - Firma Digital
- **Ley 25.326** - Protección de Datos Personales  
- **Ley 27.099** - Defensa del Consumidor
- **Código Penal** - Art. 172 bis (Estafas informáticas)

### Validez del Certificado
Los certificados `.json` generados por este protocolo:
- Son **actas de observación técnica ciudadana**
- Tienen **integridad criptográfica verificable**
- Están **vinculados a identidad real del auditor**
- Constituyen **evidencia técnica preliminar**
- **Requieren validación judicial** para uso formal

### Responsabilidad
**El auditor certificante asume responsabilidad plena** por la veracidad de la información certificada. Uso exclusivo para auditoría ética y protección del consumidor.

---

## 🔬 Ejemplo Real: Caso ganamosnet.biz

### Evidencia Capturada
```json
{
  "evidence": {
    "url": "https://ganamosnet.biz/home",
    "timestamp": "2025-12-28T05:16:10.168Z",
    "results": {
      "score": 25,
      "findings": ["🟠 BSC Network Detectada"]
    }
  },
  "integrity": "88095d343259f98cd199bde75d0df8c3378fd56e43ac5a2da0b603974941e79e"
}
```

### Certificado Generado
```bash
# Procesar evidencia
python certificar_evidencia_aee.py --modo archivo --archivo ganamosnet_evidencia.json

# Resultado: QH-CERT-ganamosnet-biz-20251228-060000.json
```

### Verificación Independiente
Cualquier perito puede verificar:
```python
# 1. Calcular hash de evidencia original
# 2. Comparar con sello en certificado  
# 3. Verificar clave pública del auditor
# 4. Validar timestamp y contexto
```

---

## 🛡️ Arquitectura Técnica

### Componentes Principales
1. **`kyber_engine.py`** - Motor de identidad soberana y sellado
2. **`certificar_evidencia_aee.py`** - Interfaz de certificación
3. **`qh_config.json`** - Configuración del auditor
4. **`LICENSE`** - Licencia AGPLv3 (software libre)

### Algoritmos Criptográficos
- **SHA3-512** - Hash post-cuántico para integridad
- **Derivación determinista** - Claves desde identidad física
- **Sellado contextual** - Evidencia + Identidad + Tiempo
- **Múltiples capas** - Robustez contra colisiones

### Características de Seguridad
- ✅ **Offline** - Sin conexión a internet requerida
- ✅ **Determinista** - Resultados reproducibles
- ✅ **Verificable** - Cualquiera puede auditar
- ✅ **Transparente** - Código fuente completo disponible
- ✅ **Post-cuántico** - Resistente a computación cuántica

---

## 🌍 Por qué es un Estándar Global

### Adaptabilidad
- **Argentina**: DNI + Ley 25.506
- **España**: NIE + eIDAS
- **México**: CURP + Ley de Firma Electrónica
- **Brasil**: CPF + MP 2.200-2
- **Cualquier país**: Documento oficial + marco legal local

### Escalabilidad Ética
```mermaid
graph TD
    A[1 Auditor] --&gt; B[1 Certificación verificable]
    B --&gt; C[100 Auditores]
    C --&gt; D[Red de inteligencia ciudadana]
    D --&gt; E[Protección colectiva contra fraudes]
```

### Innovación Clave
| Sistema Tradicional | Protocolo AEE |
|-------------------|---------------|
| Depende de corporaciones | Soberanía ciudadana |
| Código cerrado | Código abierto auditable |
| Validación centralizada | Verificación distribuida |
| Complejo, costoso | Simple, gratuito, accesible |

---

## ⚖️ Licencia y Contribución

### Licencia
- **Software**: AGPLv3 - GNU Affero General Public License v3.0
- **Certificados**: Propiedad intelectual del auditor certificante
- **Uso**: Libre para auditoría ética y protección del consumidor

### Contribuir
1. **Reportar issues** - Problemas técnicos o de seguridad
2. **Pull requests** -