from langchain_openai import ChatOpenAI
import os
import json
import certifi
import requests
import httpx
from dotenv import load_dotenv
from .risk import label_from_score

client = httpx.Client(verify=False)

def call_llm(content: str, custom_guideline: str | None = None) -> dict:
    from .prompts import BASE_SYSTEM_PROMPT

    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in",
        model="azure_ai/genailab-maas-DeepSeek-V3-0324",
        api_key="sk-qlJ246gyUqdwvaCI5R5Bag",
        http_client=client,
        temperature=0.2
    )

    messages = [
        {"role": "system", "content": "You are a compliance risk analyzer. Return valid JSON only, no prose."},
        {"role": "system", "content": BASE_SYSTEM_PROMPT},
    ]

    # Append the custom guideline as an additional system instruction if provided
    if custom_guideline and custom_guideline.strip():
        messages.append({
            "role": "system",
            "content": f"Organization-specific compliance guideline (authoritative, augmenting the above):\n{custom_guideline.strip()}"
        })

    messages.append({"role": "user", "content": content or ""})

    resp = llm.invoke(messages)
    print("Raw response:", resp)

    raw = resp.content.strip()
    print("Raw content:", raw)

    # Try to clean up JSON (remove markdown ```
    cleaned = raw.strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()

    try:
        js = json.loads(cleaned)
    except Exception as e:
        print("JSON parse error:", e)
        js = {
            "risk_score": 0.0,
            "flagged_items": [],
            "summary": "Unable to parse.",
            "risk_label": "Low"
        }

    score = float(js.get("risk_score", 0.0))
    return {
        "risk_score": max(0.0, min(1.0, score)),
        "risk_label": js.get("risk_label") or label_from_score(score),
        "flagged_items": js.get("flagged_items", []),
        "summary": js.get("summary", ""),
        "raw": js
    }
