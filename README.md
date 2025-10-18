# FastAPI + React + GPT-4 — MVP (Dockerized)

## Quick start (local)

1. Copia `.env.example` a `.env` y completa `OPENAI_API_KEY`.
2. Construye y levanta con docker-compose:
   ```
   docker-compose up --build
   ```
3. Frontend en http://localhost:3000 (sirviendo el build con nginx en el contenedor de frontend)
   Backend en http://localhost:8000

## Test curl
```
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"level":"intermedio","duration_minutes":45,"goals":"Mejorar resistencia y fuerza"}'
```

## Deploy en Fly.io (resumen)
1. Instala flyctl y logueate:
   ```
   flyctl auth login
   ```
2. Inicializa y despliega:
   ```
   flyctl init
   flyctl deploy
   ```
3. Setea el secret:
   ```
   fly secrets set OPENAI_API_KEY=sk-...
   ```

## Notas
- Nunca subas tu `OPENAI_API_KEY` a repos públicos.
- El backend pide a OpenAI que devuelva JSON — eso reduce parsing y errores, pero puede fallar si la API devuelve texto no estructurado. El código intenta extraer JSON heurísticamente.
