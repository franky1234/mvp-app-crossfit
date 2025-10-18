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
    # Note: no longer returning a mock response here — will call OpenAI APIs directly.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # First try the newer Responses API
    responses_payload = {
        "model": "gpt-4",
        "input": prompt,
        "temperature": 0.3,
        "max_output_tokens": 900,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Try Responses API across preferred models until one works
        r = None
        for model in PREFERRED_MODELS:
            try:
                responses_payload["model"] = model
                r = await client.post(RESPONSES_URL, headers=headers, json=responses_payload)
            except httpx.RequestError as exc:
                return {"error": "request_error", "detail": str(exc)}

            # If model not found or inaccessible, try next model
            if r.status_code == 404 and "model_not_found" in (r.text or ""):
                continue

            # If any other error status, break and handle below
            break

        # If Responses didn't succeed (404/model_not_found or other error), try Chat Completions across models
        if r is None or r.status_code >= 400:
            rc = None
            for model in PREFERRED_MODELS:
                chat_payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 900,
                }
                try:
                    rc = await client.post(CHAT_COMPLETIONS_URL, headers=headers, json=chat_payload)
                except httpx.RequestError as exc:
                    return {"error": "request_error", "detail": str(exc), "fallback": "chat_completions"}

                if rc.status_code == 404 and "model_not_found" in (rc.text or ""):
                    continue

                # Found usable chat response or other error; stop trying models
                break

            # If both attempts returned an HTTP error, return details
            if (r is None or r.status_code >= 400) and (rc is None or rc.status_code >= 400):
                return {
                    "error": "openai_error",
                    "status_primary": getattr(r, "status_code", None),
                    "body_primary": getattr(r, "text", None),
                    "status_fallback": getattr(rc, "status_code", None),
                    "body_fallback": getattr(rc, "text", None),
                }

            # Prefer rc (chat) if available
            data = None
            if rc is not None and rc.status_code < 400:
                try:
                    data = rc.json()
                except Exception:
                    return {"error": "invalid_json", "body": rc.text}
            else:
                try:
                    data = r.json()
                except Exception:
                    return {"error": "invalid_json", "body": r.text}
        else:
            # r is success
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError:
                return {"error": "openai_error", "status": r.status_code, "body": r.text}
            try:
                data = r.json()
            except Exception:
                return {"error": "invalid_json", "body": r.text}

    # Extract text from the response payload
    text = _extract_text_from_responses_shape(data)

    # Try to parse JSON embedded in the text
    parsed = _extract_json_from_text(text)
    if parsed is None:
        return {"error": "no_valid_json", "raw_text": text}

    # Ensure required fields exist with defaults
    parsed.setdefault("title", parsed.get("title", "Rutina personalizada"))
    parsed.setdefault("duration_minutes", parsed.get("duration_minutes"))
    parsed.setdefault("level", parsed.get("level"))
    parsed.setdefault("warmup", parsed.get("warmup", []))
    parsed.setdefault("exercises", parsed.get("exercises", []))
    parsed.setdefault("cooldown", parsed.get("cooldown", []))
    parsed.setdefault("modifications", parsed.get("modifications", {}))
    parsed["raw_text"] = text
    return parsed
