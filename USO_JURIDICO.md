# ⚖️ Guía de Uso Jurídico - Protocolo AEE v1.4

**Para abogados, fiscales y profesionales del derecho**

## 📋 Modelo de Presentación en Demanda

### Inclusión en Escrito Judicial

```legal
V. PRUEBA DIGITAL ADJUNTA

Adjunto se presenta Certificado AEE v1.4, generado según Protocolo de
Auditoría Ética y Evidencia, el cual cumple con los requisitos de la
Ley 25.506 de Firma Digital por:

1. Utilizar algoritmo hash SHA3-512 (estándar NIST FIPS 202)
2. Incluir sello temporal mediante servidores NTP oficiales
   (Google, NIST, Microsoft - consenso multi-servidor)
3. Contener identificación del auditor responsable
4. Preservar cadena de custodia digital documentada

La evidencia puede verificarse independientemente mediante:
https://github.com/quantum-humanity/aee-protocol

La integridad del documento está garantizada por hash:
[INSERTAR_HASH_DEL_CERTIFICADO]
```

### Fundamentación para Impugnaciones Técnicas

#### **Caso 1: Impugnación por "Fecha No Cierta"**
**Contraparte alega:**
> "La evidencia fue generada posteriormente al hecho"

**Usted responde:**
> "El certificado incluye timestamp consensuado por 3 servidores NTP
> oficiales (Google time.google.com, NIST time.nist.gov, Microsoft time.windows.com),
> imposible de manipular sin colusión internacional. Ref. Ley 25.506 Art. 3 - 
> Presunción de fecha cierta cuando se utilizan métodos técnicamente confiables."

#### **Caso 2: Impugnación por "Alteración Digital"**
**Contraparte alega:**
> "El archivo pudo ser modificado después de generado"

**Usted responde:**
> "El hash SHA3-512 actúa como sello digital. Cualquier modificación,
> por mínima que sea, cambiaría completamente el hash. La invariabilidad
> puede verificarse recalculando el hash con cualquier herramienta SHA3-512
> (OpenSSL, Python, etc.). Ref. Ley 25.506 Art. 7 - Presunción de integridad."

## 🔍 Flujo de Trabajo Recomendado

### Paso 1: Captura de Evidencia (Cliente o Abogado)
```bash
# El cliente o usted ejecuta:
python paquete_AEE_certificar_evidencia.py --url "https://sitio-estafa.com"
```

### Paso 2: Validación Legal (Abogado)
```bash
# Usted valida el certificado:
python paquete_AEE_validador_legal.py --certificado QH-CERT-*.json
```

### Paso 3: Generación de Informe (Abogado)
```bash
# Genera informe listo para adjuntar:
python paquete_AEE_report_generator.py --input QH-CERT-*.json --output informe_legal.txt
```

### Paso 4: Inclusión en Expediente
1. Adjuntar archivo `.json` como "Prueba Digital Original"
2. Adjuntar `informe_legal.txt` como "Informe Técnico-Legal"
3. Incluir fundamentación en escrito (ver modelo arriba)

## ⚡ Templates Rápidos

### Para Citación de Perito Informático
```legal
SOLICITO se cite como perito informático para que analice el
Certificado AEE v1.4 adjunto, específicamente para que informe:

1. Si el hash SHA3-512 garantiza la integridad del documento
2. Si el timestamp NTP multi-servidor garantiza la "fecha cierta"
3. Si el método cumple con los estándares de la Ley 25.506
```

### Para Ofrecimiento de Prueba
```legal
OFREZCO como prueba el Certificado AEE v1.4 correspondiente a
[DESCRIPCIÓN DEL CASO], el cual documenta [HECHOS RELEVANTES].

La prueba es admisible por:
- Art. 3 Ley 25.506 (Fecha cierta mediante NTP)
- Art. 7 Ley 25.506 (Integridad mediante hash criptográfico)
- Art. 172 CP (Configura estafa digital verificable)
```

## 🎯 Casos Prácticos de Aplicación

### Caso A: Estafa Financiera (Esquema Ponzi)
**Evidencia a capturar:**
- Promesas de retorno garantizado
- Ausencia de número de registro CNV
- Estructura de referidos piramidal

**Fundamento legal automático (AEE v1.4 genera):**
- Ley 26.831 Art. 1 (Mercado de Capitales)
- CNV Com. "A" 702 (Oferta Pública)
- Código Penal Art. 173 (Estafa agravada)

### Caso B: Phishing Bancario
**Evidencia a capturar:**
- URL falsa similar a banco real
- Certificado SSL inválido/autofirmado
- Solicitud de datos sensibles

**Fundamento legal automático:**
- Ley 26.388 Art. 2 (Acceso ilícito a sistema informático)
- Código Penal Art. 172 bis (Fraude informático)
- Ley 25.326 Art. 4 (Protección datos personales)

### Caso C: Contrato Digital Alterado
**Evidencia a capturar:**
- Análisis de watermarking contra reescritura por IA
- Comparación de hashes entre versiones
- Detección de manipulación semántica

**Fundamento legal:**
- Código Civil y Comercial Art. 288 (Consentimiento viciado)
- Ley 25.506 Art. 8 (Presunción de autoría/integridad)

## 📞 Soporte Técnico-Legal

### Preguntas Frecuentes

**Q: ¿Reemplaza a un perito informático?**
**R:** No, lo complementa. AEE estandariza la captura inicial, el perito profundiza.

**Q: ¿Es válido en todo el país?**
**R:** Sí, la Ley 25.506 es de aplicación nacional. Los estándares NIST/NTP son internacionales.

**Q: ¿Qué costo tiene para mis clientes?**
**R:** Cero. El software es open-source. Usted puede cobrar por su tiempo de análisis.

**Q: ¿Necesito conocimientos técnicos?**
**R:** Básicos. Siga los pasos de esta guía o solicite capacitación.

### Capacitación Disponible
- Video-tutorial: 20 minutos (disponible en GitHub)
- Guía paso a paso: Incluida en este documento
- Soporte comunitario: Issues de GitHub
- Consultoría personalizada: Contactar al autor

## ⚠️ Limitaciones y Advertencias

### El Protocolo AEE ES:
- Herramienta técnica de captura de evidencia
- Generador de documentación estandarizada
- Complemento para peritos y abogados
- Software open-source verificable

### El Protocolo AEE NO ES:
- Prueba legal concluyente por sí sola
- Sustituto de perito judicial
- Asesoramiento legal
- Garantía de éxito en juicio

## 🔄 Actualizaciones Legales

Esta guía se actualizará conforme cambie la legislación. Suscríbase a:
- Releases en GitHub
- Canal Telegram @ProtocoloAEE (próximamente)
- Newsletter legal-tech (en desarrollo)

---

**Última actualización:** Diciembre 2025  
**Compatibilidad:** Ley 25.506 y normativa vigente  
**Autor:** Franco Carricondo - DNI 35.664.619  
**Contacto profesional:** GitHub Issues o email seguro

*"La tecnología al servicio de la justicia, la justicia al servicio de la gente."*
