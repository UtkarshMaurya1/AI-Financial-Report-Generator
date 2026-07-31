import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct").strip()

if not HF_API_TOKEN:
    print("[LLM WARNING] HF_API_TOKEN is not set — check your .env file")

client = InferenceClient(model=HF_MODEL, token=HF_API_TOKEN)


def call_llm(system_prompt: str, user_content: str) -> dict:

    try:
        response = client.chat.completions.create(
            model=HF_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            max_tokens=1500,
        )
        raw_text = response.choices[0].message.content
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