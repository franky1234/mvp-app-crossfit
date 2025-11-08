# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

CrossFit workout generator MVP using FastAPI (backend) + React (frontend) with local Ollama LLM integration. The application generates personalized CrossFit routines based on user preferences (level, duration, goals).

## Architecture

### Backend (`backend/`)
- **Framework**: FastAPI with Uvicorn
- **LLM Integration**: Ollama (local llama3.1 model) via HTTP API
- **Structure**:
  - `app/main.py`: FastAPI app definition, CORS config, `/generate` endpoint
  - `app/openai_client.py`: Ollama client that sends prompts and parses JSON responses with extensive error handling and normalization
  - `app/schemas.py`: Pydantic models for request/response validation (`RoutineRequest`, `RoutineResponse`, `Exercise`)
- **Key Design**: The OpenAI client was originally built for OpenAI but has been switched to local Ollama. It includes robust JSON extraction logic that handles malformed responses by parsing text heuristically.

### Frontend (`frontend/`)
- **Framework**: React 18 + Vite
- **Structure**:
  - `src/App.jsx`: Main app component, reads API base URL from env
  - `src/components/GenerateForm.jsx`: Form for workout generation with state management
  - `src/main.jsx`: React app mounting with error handling
- **Build**: Vite builds to `dist/`, served by `serve` package in production container

### Deployment
- **Local**: Docker Compose with host networking for backend (to access Ollama on localhost:11434)
- **Production**: Fly.io configuration (`fly.toml`) for backend deployment

## Common Commands

### Development

#### Start entire stack (Docker)
```bash
docker-compose up --build
```
Access: Frontend at http://localhost:3000, Backend at http://localhost:8000

#### Backend only (local development)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend only (local development)
```bash
cd frontend
npm install
npm run dev  # Vite dev server, typically on port 5173
```

#### Build frontend for production
```bash
cd frontend
npm run build  # outputs to dist/
npm run preview  # preview production build locally
```

### Testing

#### Test backend endpoint manually
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"level":"intermedio","duration_minutes":45,"goals":"Mejorar resistencia y fuerza"}'
```

### Deployment

#### Deploy to Fly.io
```bash
# Login
flyctl auth login

# Initialize app (first time)
flyctl init

# Set OpenAI API key secret (if using OpenAI instead of Ollama)
fly secrets set OPENAI_API_KEY=sk-...

# Deploy
flyctl deploy
```

## Environment Variables

### Backend
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://127.0.0.1:11434`)
- `OLLAMA_MODEL`: Model name to use (default: `llama3.1:latest`)
- `OPENAI_API_KEY`: Legacy, preserved for compatibility but not used with Ollama

### Frontend
- `VITE_API_BASE`: Backend API URL (default: `http://localhost:8000`)

## Key Implementation Details

### LLM Integration
The app uses Ollama's `/api/generate` endpoint with `format: "json"` to enforce JSON output. The response parser (`openai_client.py`):
1. Extracts text from Ollama response (`response` field)
2. Searches for JSON object boundaries `{...}` in the text
3. Normalizes warmup/cooldown to lists of strings
4. Normalizes exercises to conform to `Exercise` schema with defaults
5. Returns structured dict or error object

### CORS Configuration
Backend allows requests from `http://localhost:3000` and `http://127.0.0.1:3000` for local development. Update `origins` list in `backend/app/main.py` for production domains.

### Docker Networking
Backend uses `network_mode: host` in docker-compose to access Ollama running on the host machine's localhost:11434. This is Linux-specific; on macOS/Windows use `host.docker.internal` instead.

## Codebase Conventions

- Backend uses async/await for HTTP operations (FastAPI + httpx)
- Pydantic for all data validation and serialization
- Frontend uses functional React components with hooks
- Error responses include detailed diagnostic info (sanitize before production)
- Spanish language used in prompts and UI text
