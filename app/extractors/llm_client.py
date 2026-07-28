import os 
import json, httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_llm(system_prompt: str, user_content:str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "message": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0,
    }

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(OPENROUTER_URL, headers=headers, payload=payload)
            resp.raise_for_status()
            raw_text = resp.json()['choices'][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return {}

    return _safe_json_parse(raw_text)

def _safe_json_parse(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("json", "", 1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[LLM WARNING] Could not parse JSON:\n{text[:300]}")
        return {}
