import os
import json
import httpx
from typing import Dict, Any, Optional

RESPONSES_URL = "https://api.openai.com/v1/responses"
CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"

# Preferred models to try in order when a model is not available / accessible.
PREFERRED_MODELS = ["gpt-4", "gpt-4o", "gpt-3.5-turbo"]


def _extract_text_from_responses_shape(data: Dict[str, Any]) -> str:
    """Attempt to extract the human-readable text from various OpenAI response shapes."""
    # Responses API often uses 'output' with nested content
    output = data.get("output") or data.get("choices")
    if isinstance(output, list) and len(output) > 0:
        candidate = output[0]
        if isinstance(candidate, dict):
            # check nested content
            content = candidate.get("content")
            if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                return content[0].get("text", "") or ""
            return candidate.get("text", "") or ""
        return str(candidate)
    # Chat/completions shape
    choices = data.get("choices")
    if isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            # chat completions: message.content
            message = first.get("message") or first.get("delta")
            if isinstance(message, dict):
                return message.get("content", "") or message.get("text", "") or ""
            # older completions: text field
            return first.get("text", "") or ""
    # fallback: stringify the whole payload
    try:
        return json.dumps(data)
    except Exception:
        return ""


def _extract_json_from_text(s: str) -> Optional[Dict[str, Any]]:
    s = (s or "").strip()
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(s[start : end + 1])
        except Exception:
            pass
    return None


async def generate_workout(prompt: str, api_key: str) -> Dict[str, Any]:
    # Switch to local Ollama (llama3.1). We ignore api_key intentionally.
    # Ollama generate API: POST http://localhost:11434/api/generate
    # payload: { model: "llama3.1", prompt, stream: false, options: { temperature } }
    url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434") + "/api/generate"
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        "prompt": prompt,
        "stream": False,
        # Ask Ollama to emit strict JSON if supported
        "format": "json",
        "options": {
            "temperature": 0.3,
            "top_p": 0.95,
            # keep output within bounds to avoid extremely long generations
            "num_predict": 1200,
            # Optimize for faster generation
            "num_ctx": 2048
        }
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            resp = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            return {"error": "request_error", "detail": repr(exc), "url": url}

    if resp.status_code >= 400:
        return {"error": "ollama_error", "status": resp.status_code, "body": resp.text}

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    # Extract text: Ollama /api/generate returns { response: "..." }
    text = (data.get("response") or "").strip()

    # Try to parse JSON embedded in the text
    parsed = _extract_json_from_text(text)
    if parsed is None:
        return {"error": "no_valid_json", "raw_text": text}

    # Ensure required fields exist with defaults
    # Normalize warmup/cooldown to list[str]
    try:
        if isinstance(parsed.get("warmup"), list):
            norm_warmup = []
            for it in parsed["warmup"]:
                if isinstance(it, str):
                    norm_warmup.append(it)
                elif isinstance(it, dict):
                    name = str(it.get("name", "")) if it.get("name") is not None else ""
                    sets = it.get("sets")
                    rest = it.get("rest_seconds")
                    notes = it.get("notes")
                    parts = [p for p in [name, f"sets:{sets}" if isinstance(sets, int) else None, f"rest:{rest}s" if isinstance(rest, int) else None, f"notes:{notes}" if notes else None] if p]
                    norm_warmup.append(" | ".join(parts) if parts else json.dumps(it))
                else:
                    norm_warmup.append(str(it))
            parsed["warmup"] = norm_warmup
    except Exception:
        pass

    try:
        if isinstance(parsed.get("cooldown"), list):
            norm_cooldown = []
            for it in parsed["cooldown"]:
                if isinstance(it, str):
                    norm_cooldown.append(it)
                elif isinstance(it, dict):
                    name = str(it.get("name", "")) if it.get("name") is not None else ""
                    sets = it.get("sets")
                    rest = it.get("rest_seconds")
                    notes = it.get("notes")
                    parts = [p for p in [name, f"sets:{sets}" if isinstance(sets, int) else None, f"rest:{rest}s" if isinstance(rest, int) else None, f"notes:{notes}" if notes else None] if p]
                    norm_cooldown.append(" | ".join(parts) if parts else json.dumps(it))
                else:
                    norm_cooldown.append(str(it))
            parsed["cooldown"] = norm_cooldown
    except Exception:
        pass

    # Normalize exercises list item types
    try:
        if isinstance(parsed.get("exercises"), list):
            norm_ex = []
            for ex in parsed["exercises"]:
                if not isinstance(ex, dict):
                    ex = {"name": str(ex), "sets": 1, "reps_or_time": ""}
                name = ex.get("name")
                sets = ex.get("sets")
                reps = ex.get("reps_or_time")
                rest = ex.get("rest_seconds")
                notes = ex.get("notes")
                ex_norm = {
                    "name": str(name) if name is not None else "Ejercicio",
                    "sets": int(sets) if isinstance(sets, (int, float, str)) and str(sets).isdigit() else (sets if isinstance(sets, int) else 1),
                    "reps_or_time": str(reps) if reps is not None else "",
                }
                if rest is not None:
                    try:
                        ex_norm["rest_seconds"] = int(rest)
                    except Exception:
                        pass
                if notes is not None:
                    ex_norm["notes"] = str(notes)
                norm_ex.append(ex_norm)
            parsed["exercises"] = norm_ex
    except Exception:
        pass

    # Now set defaults for any missing fields
    parsed.setdefault("title", parsed.get("title", "Rutina personalizada"))
    parsed.setdefault("duration_minutes", parsed.get("duration_minutes"))
    parsed.setdefault("level", parsed.get("level"))
    parsed.setdefault("warmup", parsed.get("warmup", []))
    parsed.setdefault("exercises", parsed.get("exercises", []))
    parsed.setdefault("cooldown", parsed.get("cooldown", []))
    parsed.setdefault("modifications", parsed.get("modifications", {}))
    parsed["raw_text"] = text
    return parsed
