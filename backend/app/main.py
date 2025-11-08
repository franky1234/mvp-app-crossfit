from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from .openai_client import generate_workout
from .schemas import RoutineRequest, RoutineResponse

app = FastAPI(title="CrossFit GPT-4 API")

# CORS: permitir peticiones desde el frontend durante desarrollo
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate", response_model=RoutineResponse)
async def generate(r: RoutineRequest):
    # API key is optional now; Ollama does not require it. Preserve env read for compatibility.
    api_key = os.getenv('OPENAI_API_KEY', '')

    prompt = (
        f"Crea una rutina CrossFit de {r.duration_minutes} min, nivel {r.level}. Objetivo: {r.goals}.\n"
        f"Responde SOLO con JSON válido:\n"
        f"{{"
        f'  "title": "nombre de la rutina",\n'
        f'  "duration_minutes": {r.duration_minutes},\n'
        f'  "level": "{r.level}",\n'
        f'  "warmup": ["ejercicio1", "ejercicio2"],\n'
        f'  "exercises": [{{"name": "ejercicio", "sets": 3, "reps_or_time": "10 reps", "rest_seconds": 60}}],\n'
        f'  "cooldown": ["ejercicio1"],\n'
        f'  "modifications": {{"principiante": "texto", "avanzado": "texto"}}\n'
        f"}}"
    )

    try:
        result = await generate_workout(prompt, api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # result is expected to be dict with structured fields
    if result.get("error"):
        # Include the OpenAI client error payload in the response for debugging.
        # This is temporary — remove or sanitize before production to avoid leaking details.
        raise HTTPException(status_code=502, detail=result)

    return result
