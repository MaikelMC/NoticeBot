# 🤖 Kynari Bot — Telegram Intelligent Search Bot

**Kynari** es un bot de Telegram inteligente que busca información actualizada en la web y la resume usando **Mistral AI**. Puedes conversar con él de forma natural o usar comandos específicos.

## ✨ Características

- 🔍 **Búsqueda web** usando DuckDuckGo (máximo 8 resultados)
- 🤖 **Resúmenes inteligentes** con Mistral AI (modelo `mistral-large-latest`)
- 💬 **Modo conversacional**: escribe cualquier pregunta y el bot la procesa automáticamente
- 📝 **Respuestas formateadas** con Markdown
- ⚡ **Rápido y eficiente** con soporte asíncrono
- 🛡️ **Manejo de errores** robusto (rate limits, timeouts, fallos de API)
- 🌐 **Idioma**: responde siempre en español

## 📋 Requisitos

- Python 3.11 o superior
- Una cuenta y API key de [Mistral AI](https://console.mistral.ai/)
- Un token de bot de [@BotFather](https://t.me/BotFather) en Telegram

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd kynari-bot
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
MISTRAL_API_KEY=tu_api_key_de_mistral
```

### 5. Ejecutar el bot

```bash
python bot.py
```

## 🎮 Comandos

| Comando | Descripción |
|---|---|
| `/start` | Mensaje de bienvenida |
| `/help` | Lista de comandos y ayuda |
| `/buscar <tema>` | Busca información sobre un tema específico |

### 💬 Modo conversacional

Simplemente **escribe cualquier mensaje** y Kynari lo interpretará como una solicitud de búsqueda:

```
Usuario: ¿Qué está pasando con la inteligencia artificial en 2025?
Kynari: 🔍 [busca en la web y responde con un resumen estructurado]
```

## 🏭 Despliegue en Render

### Usando webhooks (recomendado para producción)

1. Sube el código a GitHub/GitLab
2. En [Render](https://render.com/), crea un nuevo **Web Service**
3. Conecta tu repositorio
4. Configura:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Agrega las variables de entorno en Render:
   - `TELEGRAM_BOT_TOKEN`
   - `MISTRAL_API_KEY`
   - `USE_WEBHOOK=true`
   - `WEBHOOK_URL=https://tuapp.onrender.com`
6. Despliega

> **Nota:** El `Procfile` y `runtime.txt` ya están incluidos para facilitar el despliegue en Render.

### Usando polling (desarrollo local)

Simplemente ejecuta `python bot.py` con `USE_WEBHOOK=false` en tu `.env`.

## 🔧 Estructura del proyecto

```
kynari-bot/
├── bot.py                 # Archivo principal (entry point)
├── config.py              # Configuración y variables de entorno
├── handlers.py            # Manejadores de comandos y mensajes
├── tools/
│   ├── __init__.py        # Inicializador del paquete
│   ├── web_search.py      # Herramienta de búsqueda web (DuckDuckGo)
│   └── mistral_ai.py      # Integración con Mistral AI
├── requirements.txt       # Dependencias de Python
├── runtime.txt            # Versión de Python para Render
├── Procfile               # Configuración para Render
├── .env.example           # Plantilla de variables de entorno
└── README.md              # Este archivo
```

## ⚙️ Configuración avanzada

Puedes ajustar estos parámetros en tu `.env`:

| Variable | Descripción | Default |
|---|---|---|
| `MAX_SEARCH_RESULTS` | Número máximo de resultados de búsqueda | `8` |
| `MISTRAL_MODEL` | Modelo de Mistral AI a usar | `mistral-large-latest` |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `BOT_USERNAME` | Nombre de usuario del bot | `KynariBot` |

## 🛡️ Licencia

MIT

---

Hecho con ❤️ por [Tu Nombre]
