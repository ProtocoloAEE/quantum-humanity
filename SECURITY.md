# 🔒 Política de Seguridad

## 📞 Reportando una Vulnerabilidad

**NO reportes vulnerabilidades de seguridad a través de issues públicos de GitHub.**

Si descubres una vulnerabilidad de seguridad en el Protocolo AEE:

1. **Envía un email a:** `seguridad@quantum-humanity.org` (próximamente)
   - O usa el formulario seguro en el sitio web oficial
   
2. **Incluye en tu reporte:**
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir
   - Impacto potencial
   - Sugerencias de mitigación (si las tienes)

3. **Tiempo de respuesta:**
   - Confirmación: 24-48 horas
   - Evaluación: 3-5 días hábiles
   - Parche: Dependiendo de complejidad (1-4 semanas)

4. **Recompensas:**
   - Actualmente no ofrecemos bug bounty program
   - Reconocimiento público (si el reportero lo autoriza)
   - Mención en CHANGELOG.md

## 🔐 Medidas de Seguridad Implementadas

### Para Usuarios
- **Procesamiento 100% offline**: Tus datos nunca salen de tu máquina
- **Sin telemetría**: No recolectamos información de uso
- **Código abierto**: Todo es auditable por cualquiera
- **Hashes verificables**: Puedes validar la integridad del software

### Para Desarrolladores
- **Dependencias escaneadas**: Regularmente auditamos `requirements.txt`
- **Sanitización de entrada**: Todas las entradas de usuario son validadas
- **Manejo seguro de errores**: No se filtran datos sensibles en logs
- **Pruebas de seguridad**: Test suite incluye casos de seguridad básicos

### Para el Proyecto
- **Commits firmados**: (Próximamente) Todos los commits serán GPG-signed
- **2FA requerido**: Para colaboradores con acceso de escritura
- **Reviews obligatorios**: Ningún PR se mergea sin al menos 1 review
- **CI/CD con scanning**: GitHub Actions con análisis de seguridad

## 🛡️ Guía de Seguridad para Usuarios

### Protege Tu Certificado
```bash
# Recomendado: Encriptar certificados sensibles
gpg --encrypt --recipient "tu@email.com" certificado.json

# Almacenar en lugar seguro
mv certificado.json.gpg ~/Documentos/Evidencias_Seguras/
```

### Verifica Descargas
```bash
# Verificar hash SHA256 de descargas
echo "HASH_ESPERADO  archivo.zip" | sha256sum -c
```

### Uso en Entornos Sensibles
- Ejecuta en máquina air-gapped si la evidencia es crítica
- Usa VPN para capturas de sitios sensibles
- Considera usar máquina virtual desechable

## 🚨 Vulnerabilidades Conocidas

### Actualmente Ninguna
No tenemos vulnerabilidades de seguridad conocidas en la versión actual.

### Historial de Vulnerabilidades Corregidas

#### [v1.3.1] - 2025-12-25
- **CVE simulado-2025-1001**: Validación insuficiente de URLs
  - **Impacto**: Posible SSRF en modo interactivo
  - **Parche**: Sanitización estricta + lista blanca de protocolos
  - **Gravedad**: Media

#### [v1.2.0] - 2025-12-10  
- **CVE simulado-2025-1002**: Inyección JSON en reportes
  - **Impacto**: Posible ejecución de código al generar PDF
  - **Parche**: Escape de caracteres especiales
  - **Gravedad**: Alta

## 📚 Mejores Prácticas Recomendadas

### Para Ciudadanos/Auditores
1. **Actualiza regularmente**: `git pull origin main`
2. **Usa entornos aislados**: Docker o venv
3. **Verifica certificados**: Antes de presentar en juicio
4. **Backup seguro**: De tus certificados importantes

### Para Abogados/Estudios
1. **Capacita a tu equipo**: En uso básico del protocolo
2. **Establece protocolos internos**: Para manejo de evidencia digital
3. **Colabora con peritos**: AEE complementa, no reemplaza, peritos
4. **Mantén registros**: De qué herramienta generó cada evidencia

### Para Desarrolladores/Contribuidores
1. **Sigue secure coding guidelines**: Del repositorio
2. **Escribe tests de seguridad**: Para nuevas funcionalidades
3. **Revisa dependencias**: `pip-audit` regularmente
4. **Participa en reviews**: De código de otros contribuidores

## 🌐 Coordinación de Seguridad

### Equipo de Seguridad
- **Líder de Seguridad**: Franco Carricondo
- **Contacto Principal**: GitHub Issues (etiqueta `security`)
- **Horario de Respuesta**: Lunes a Viernes 9-18hs (ART)

### Proceso de Divulgación Responsable
1. Reporter notifica a equipo de seguridad
2. Equipo confirma recepción en 48h
3. Equipo investiga y desarrolla parche
4. Parche se prueba internamente
5. Se lanza actualización de seguridad
6. Se publica advisory (después de 30 días de parche disponible)

### Embargos
- **Período de embargo típico**: 30 días después de parche disponible
- **Excepciones**: Vulnerabilidades críticas en producción
- **Coordinación**: Con reporter y posibles afectados

## 📜 Política de Retención de Datos

### Lo que NO guardamos:
- Certificados generados por usuarios
- URLs auditadas por usuarios  
- Datos personales de usuarios
- Logs de ejecución (más allá de errores anónimos)

### Lo que SÍ guardamos (en GitHub):
- Código fuente del proyecto
- Issues y discusiones técnicas
- Registro de commits
- Documentación

## 🤝 Reconocimientos

Agradecemos a todos los que reportan vulnerabilidades de forma responsable.
Los créditos se darán (con permiso) en:
- CHANGELOG.md (sección de seguridad)
- README.md (agradecimientos)
- Advisory de GitHub (si aplica)

---

**Última actualización:** Diciembre 2025  
**Próxima revisión:** Marzo 2026  
**Contacto de seguridad:** Issues de GitHub con etiqueta `security`

*La seguridad es un proceso, no un producto.*
