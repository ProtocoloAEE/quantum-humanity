# 🔐 Protocolo AEE (Auditoría Ética y Evidencia) v1.4

![Quantum Humanity](https://img.shields.io/badge/Quantum-Humanity-blue)
![Protocolo AEE](https://img.shields.io/badge/Protocolo-AEE_v1.4-green)
![Licencia AGPLv3](https://img.shields.io/badge/Licencia-AGPLv3-lightgrey)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-yellow)

**Sistema de certificación soberana para evidencia digital con validez legal potencial**

## ✨ Características Principales

### 🛡️ Módulo de Blindaje Legal (v1.4)
El protocolo ha sido fortalecido para generar evidencia digital con un alto grado de admisibilidad en procesos judiciales, incorporando los siguientes avances:

- **Sellado de Tiempo Auditable**: Conforme a la Ley 25.506 (Firma Digital), el sistema utiliza un consenso de múltiples servidores NTP oficiales (Google, NIST, etc.) para establecer una "fecha cierta", neutralizando posibles impugnaciones sobre la hora de la captura.
- **Motor de Riesgo con Fundamento Jurídico**: Cada hallazgo técnico es automáticamente mapeado contra legislación argentina vigente (Ley de Mercado de Capitales, Ley de Defensa del Consumidor, Código Penal), proveyendo un fundamento legal explícito para la evaluación de riesgo.
- **Estructura de Acta Probatoria**: Los certificados JSON ahora se generan como "Actas de Observación Técnica", incluyendo declaraciones juradas, detalles para la cadena de custodia y secciones claras de hechos, derecho y prueba.
- **Generador de Informes para Abogados**: El paquete incluye `report_generator.py`, una herramienta que traduce el certificado técnico a un informe en texto plano, listo para ser integrado en una denuncia formal.

### 🔐 Criptografía Post-Cuántica
- **SHA3-512 Determinístico**: Hash inmutable para integridad de evidencia
- **Firmas Digitales**: Compatible con estándares PKI y futuras migraciones post-cuánticas
- **Watermarking Resistente**: Detección de manipulación por IA (sobrevive reescritura GPT-4/Claude)

### 👤 Soberanía Ciudadana
- **Identidad Verificable**: Vinculación a DNI/identificación oficial
- **Auditoría Descentralizada**: Cualquier ciudadano puede generar certificados válidos
- **Transparencia Total**: Código abierto, verificable por cualquiera

## 🚀 Para Abogados y Fiscales: Cómo Usar AEE en su Práctica

### **Flujo de Trabajo Integrado**
```
Cliente víctima → Abogado recibe caso → Ejecuta AEE v1.4 → Adjunta certificado a demanda
```

### **Valor Profesional Concreto**

| Problema Legal | Solución AEE v1.4 | Beneficio |
|----------------|-------------------|-----------|
| "Es solo una captura de pantalla" | Certificado con hash SHA3-512 + timestamp NTP | **Prueba inmutable** |
| "No tiene fecha cierta" | Sellado 3 servidores NTP oficiales | **Fecha judicialmente válida** |
| "No fundamenta la ilegalidad" | Mapeo automático a legislación vigente | **Argumentación legal lista** |
| "Cadena de custodia débil" | Estructura de acta con declaración jurada | **Cadena de custodia digital** |

### **Implementación Rápida**
```bash
# 1. Instalación (30 segundos)
pip install -r requirements.txt

# 2. Certificar caso (2 minutos)
python paquete_AEE_certificar_evidencia.py --url "https://sitio-sospechoso.com"

# 3. Generar informe para demanda (30 segundos)
python paquete_AEE_report_generator.py --input certificado.json
```

## 📁 Estructura del Proyecto

```
aee-protocol/
├── README.md                         # Este archivo
├── USO_JURIDICO.md                   # Guía completa para uso legal
├── CHANGELOG.md                      # Historial de versiones
├── SECURITY.md                       # Política de seguridad
├── CONTRIBUTING.md                   # Guía para contribuir
├── requirements.txt                  # Dependencias Python
├── paquete_AEE_certificar_evidencia.py  # Módulo principal
├── paquete_AEE_validador_legal.py    # Validador de cumplimiento legal
├── paquete_AEE_report_generator.py   # Generador de informes
├── paquete_AEE_legal_compliance.py   # Verificación de normativas
└── paquete_AEE_INSTRUCCIONES.txt     # Instrucciones detalladas
```

## ⚡ Comenzar Rápidamente

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/quantum-humanity/aee-protocol.git
cd aee-protocol

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico
```python
# Ejecutar certificación interactiva
python paquete_AEE_certificar_evidencia.py

# O usar modo directo
python paquete_AEE_certificar_evidencia.py --url "https://ejemplo.com" --riesgo 75
```

### Generar Informe Legal
```bash
python paquete_AEE_report_generator.py --certificado QH-CERT-ejemplo.json
```

## ⚖️ Compatibilidad Legal

El Protocolo AEE v1.4 está diseñado para cumplir con:

- **Ley 25.506** - Firma Digital Argentina (Arts. 3, 7, 8)
- **Ley 26.831** - Mercado de Capitales
- **Ley 24.240** - Defensa del Consumidor
- **Código Penal** - Arts. 172 (Estafa), 173 (Estafa Agravada), 310 (Ejercicio Ilegal de Actividad)
- **Ley 25.326** - Protección de Datos Personales

## 👥 Para Desarrolladores

### Extender el Protocolo
```python
from paquete_AEE_legal_compliance import ComplianceLey25506

# Verificar cumplimiento de un certificado
validador = ComplianceLey25506()
resultado = validador.verificar_cumplimiento(certificado)
```

### API Simple
```python
# Generar certificado programáticamente
certificado = generar_certificado(
    url="https://sitio-a-auditar.com",
    hallazgos=["falta_cuit", "retornos_garantizados"],
    auditor={"nombre": "Auditor", "dni": "XXXXXXXX"}
)
```

## 📊 Casos de Uso Comprobados

### 1. **Estafas Financieras** (ganamosnet.biz)
- Detección: Ausencia CUIT + Retornos garantizados
- Riesgo: 95/100 (Crítico)
- Acción: Denuncia CNV + UFECI

### 2. **Phishing/Suplantación**
- Detección: Certificado SSL inválido + logos falsos
- Riesgo: 80/100 (Alto)
- Acción: Takedown request + alerta a usuarios

### 3. **Contenido Manipulado por IA**
- Detección: Watermark sobrevive reescritura LLM
- Riesgo: Variable según contexto
- Acción: Prueba de alteración digital

## 🛡️ Seguridad y Privacidad

- **Sin tracking**: El protocolo funciona 100% offline
- **Datos locales**: Todo se procesa en tu máquina
- **Sin backdoors**: Código abierto auditable
- **Responsabilidad limitada**: Herramienta técnica, no consejo legal

## 🤝 Contribuir

¿Quieres mejorar el protocolo? Lee [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Reportar bugs
- Sugerir features
- Enviar pull requests
- Traducir documentación

## 📞 Contacto Seguro

**Para consultas profesionales:**
- Issues de GitHub: Para reportes técnicos
- Email: [Usar formulario seguro en futura versión web]
- Telegram: @ProtocoloAEE (canal oficial - próximamente)

**No compartas datos personales en issues públicos.**

## 📜 Licencia

Este proyecto está bajo la licencia **AGPLv3**. Ver [LICENSE](LICENSE) para detalles.

---

**💡 Recordatorio:** El Protocolo AEE es una herramienta técnica para generar evidencia digital. No constituye asesoramiento legal. Para cuestiones jurídicas, consulta con un abogado especializado.

**🇦🇷 La soberanía digital se ejerce, no se delega.**
