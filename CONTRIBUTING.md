# 👥 Guía de Contribución

¡Gracias por tu interés en contribuir al Protocolo AEE! 
Esta guía te ayudará a colaborar efectivamente.

## 🎯 ¿Cómo Puedo Contribuir?

### 1. Reportar Bugs
Encontraste un error? ¡Ayúdanos a mejorar!

**Antes de reportar:**
- [ ] Verifica que no sea un error de configuración tuya
- [ ] Busca issues existentes para evitar duplicados
- [ ] Prueba con la última versión del código

**Template para reporte de bug:**
```markdown
## Descripción del Bug
[Descripción clara y concisa]

## Pasos para Reproducir
1. Ir a '...'
2. Click en '....'
3. Scroll hasta '....'
4. Ver error

## Comportamiento Esperado
[Lo que debería pasar]

## Comportamiento Actual  
[Lo que realmente pasa]

## Contexto Adicional
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python: [e.g. 3.9.1]
- Versión AEE: [e.g. 1.4.0]
```

### 2. Sugerir Mejoras
Tienes ideas para nuevas características?

**Template para sugerencia:**
```markdown
## Problema/Oportunidad
[Descripción del problema que resuelve o oportunidad]

## Solución Propuesta
[Descripción detallada de la solución]

## Alternativas Consideradas
[Otras soluciones que consideraste]

## Impacto Esperado
[Quién se beneficia y cómo]
```

### 3. Enviar Código (Pull Requests)
¿Quieres implementar algo directamente?

## 🛠️ Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.8+
- Git
- Virtualenv (recomendado)

### Pasos
```bash
# 1. Fork el repositorio
# 2. Clona tu fork
git clone https://github.com/TU_USUARIO/aee-protocol.git
cd aee-protocol

# 3. Crea entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 4. Instala dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias de desarrollo

# 5. Crea una rama para tu feature
git checkout -b feature/nombre-de-tu-feature
```

## 📝 Convenciones de Código

### Estilo de Código
- Seguimos **PEP 8** para Python
- Usamos **black** para formateo automático
- **mypy** para type checking (opcional pero recomendado)

### Commits
- Usa **mensajes de commit descriptivos**
- Referencia issues: `git commit -m "fix: corrige bug #123"`
- Prefix según tipo:
  - `feat:` Nueva funcionalidad
  - `fix:` Corrección de bug
  - `docs:` Cambios en documentación
  - `style:` Formato, puntos y coma, etc. (no afecta código)
  - `refactor:` Cambio que no arregla bug ni añade feature
  - `test:` Añadir o corregir tests
  - `chore:` Cambios en build, config, etc.

### Tests
- Añade tests para nuevas funcionalidades
- Mantén cobertura >80%
- Ejecuta tests antes de commit:
  ```bash
  python -m pytest tests/ --cov=src --cov-report=term-missing
  ```

## 🔄 Proceso de Pull Request

### 1. Prepara tu PR
```bash
# Actualiza tu rama con main
git fetch origin
git rebase origin/main

# Ejecuta tests y formateo
python -m pytest
black src/
flake8 src/

# Commit
git add .
git commit -m "feat: añade nueva funcionalidad X"

# Push
git push origin feature/nombre-de-tu-feature
```

### 2. Crea el PR en GitHub
- Usa el template de PR
- Describe claramente los cambios
- Referencia issues relacionados
- Incluye screenshots si aplica

### 3. Revisión
- Mantén el PR enfocado en un solo cambio
- Responde a comentarios de revisores
- Haz updates según feedback
- Mantén el PR actualizado con main

### 4. Merge
- Requiere al menos 1 review aprobatorio
- Todos los tests deben pasar
- El mantenedor hará el merge

## 🏗️ Estructura del Proyecto

```
aee-protocol/
├── src/                    # Código fuente principal
│   ├── core/              # Módulos core del protocolo
│   ├── legal/             # Módulos de compliance legal
│   ├── crypto/            # Módulos criptográficos
│   └── utils/             # Utilidades compartidas
├── tests/                 # Tests automatizados
├── docs/                  # Documentación
├── examples/              # Ejemplos de uso
└── tools/                 # Herramientas de desarrollo
```

## 📚 Áreas que Necesitan Ayuda

### Prioridad Alta
1. **Traducciones**: Español → Inglés, Portugués
2. **Tests**: Mejorar cobertura de código
3. **Documentación**: Tutoriales paso a paso

### Prioridad Media
1. **UI/UX**: Interfaz gráfica simple
2. **Integraciones**: Plugins para navegadores
3. **API**: REST API para uso remoto

### Prioridad Baja  
1. **Mobile**: App para iOS/Android
2. **CLI**: Mejores herramientas de línea de comandos
3. **Plugins**: Para otras herramientas forenses

## 🌍 Traducciones

### Guía para Traductores
1. Traduce archivos `.md` en `docs/`
2. Mantén el tono técnico pero accesible
