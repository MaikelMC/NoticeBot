# PROMPT PARA OPENCODE / CURSOR / CLAUDE

Crea un proyecto completo de Bot de Telegram llamado **Kynari Bot** con las siguientes especificaciones:

### Requisitos técnicos:
- Python 3.11+
- Usa `python-telegram-bot` versión 20+ en modo async
- Integra Mistral AI (mistralai library)
- Usa `duckduckgo-search` para buscar información en la web
- Estructura limpia con carpetas (tools/, handlers/, etc.)

### Funcionalidades obligatorias:

1. **Comandos básicos**:
   - /start → Mensaje de bienvenida profesional
   - /help → Lista de comandos disponibles
   - /buscar <tema> → Busca información sobre el tema

2. **Modo Conversacional**:
   - El usuario puede escribir cualquier texto y el bot debe interpretarlo como una solicitud de búsqueda.
   - El bot debe buscar en la web, enviar la información a Mistral para que la resuma de forma clara, estructurada y en español.
   - Respuestas bien formateadas (usando Markdown).

3. **Herramientas**:
   - Herramienta de búsqueda web robusta (máximo 5-8 resultados).
   - Prompt bien optimizado para Mistral que incluya: resumen claro, puntos clave, fuentes si es posible.

4. **Manejo de Errores**:
   - Manejar rate limits de Mistral y Telegram.
   - Mensajes amigables cuando no pueda responder.

### Estructura del proyecto:
- `bot.py` (archivo principal)
- `config.py`
- `handlers.py`
- `tools/web_search.py`
- `tools/mistral_ai.py`
- `requirements.txt`
- `runtime.txt`
- `Procfile` (para Render)
- `.env.example`

Incluye:
- Sistema de logging
- Manejo correcto de webhooks
- Comentarios claros en el código
- README.md con instrucciones de instalación y despliegue

Quiero que el bot sea **profesional, rápido y útil**, orientado a búsqueda de información actualizada.

Genera todo el código listo para copiar y pegar en los archivos correspondientes.
