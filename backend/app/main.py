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
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set on server")

    prompt = (
        f"Genera una rutina de CrossFit de {r.duration_minutes} minutos para nivel {r.level}. "
        f"Objetivos: {r.goals}. Devuelve un JSON válido con los campos: title, duration_minutes, level, "
        "warmup (lista), exercises (lista de objetos con name, sets, reps_or_time, rest_seconds, notes), "
        "cooldown (lista), modifications (con secciones para principiante y avanzado). "
        "Si no puedes generar JSON válido, responde únicamente con: {\"error\": \"No JSON\"}."
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
