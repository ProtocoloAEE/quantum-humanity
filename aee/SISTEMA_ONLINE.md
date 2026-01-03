# 🟢 SISTEMA ONLINE

## Estado del Sistema AEE Protocol v2.5.0

**Fecha:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

### ✅ Servicios Activos

1. **API FastAPI**
   - Estado: ✅ ONLINE
   - URL: http://localhost:8000
   - Health Check: http://localhost:8000/api/v1/health
   - Endpoint de Verificación: http://localhost:8000/api/v1/verify/{cert_id}

2. **Bot de Telegram @CertificadorOficialBot**
   - Estado: ✅ ONLINE
   - Token: Configurado
   - Modo: Polling activo
   - Listo para recibir certificaciones

### 🚀 Comandos de Inicio

Si necesitas reiniciar los servicios:

**API:**
```bash
cd C:\Users\WIN11\Documents\descargas\aee-protocol
python -m uvicorn aee.api.fastapi_server:app --host 0.0.0.0 --port 8000
```

**Bot:**
```bash
cd C:\Users\WIN11\Documents\descargas\aee-protocol
python aee/telegram_bot.py
```

### 📱 Uso del Bot

1. Abre Telegram
2. Busca: @CertificadorOficialBot
3. Envía: `/start`
4. Envía una imagen o PDF para certificar

### 🔗 Verificación

Los certificados se pueden verificar en:
- http://localhost:8000/api/v1/verify/{ID}

---

**SISTEMA OPERATIVO Y LISTO PARA MONETIZAR** 🎯

