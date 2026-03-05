import json
import re
from groq import Groq
import os
from dotenv import load_dotenv
from llm.prompts import (
    ITINERARY_GENERATION_PROMPT,
    BUDGET_BREAKDOWN_PROMPT,
)

load_dotenv()

# ── Groq client ───────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def _call_llm(prompt: str, max_tokens: int = 2048) -> str:
    """Core LLM call — raises exception on failure."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def _clean_json(raw: str) -> str:
    """Extract valid JSON block from LLM response."""
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)
    raw = raw.strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start:end+1]
    return raw


def _parse_json_safe(raw: str) -> dict | None:
    """Try to parse JSON, return None on failure."""
    try:
        cleaned = _clean_json(raw)
        return json.loads(cleaned)
    except Exception:
        return None


def extract_intent(user_input: str) -> dict:
    """Extract structured travel intent from raw user input."""

    prompt = f"""You are a travel assistant. Extract travel details from the user message.

User message: "{user_input}"

Return ONLY a valid JSON object — no explanation, no markdown, no extra text:
{{
  "destination": "city name as string, or null if not mentioned",
  "days": number or null,
  "budget": number or null,
  "budget_currency": "INR",
  "mood": "one of: adventure, chill, romantic, family, culture or null",
  "constraints": [],
  "is_refinement": false
}}

Rules:
- "Weekend" trips → days = 2
- Budget must be a plain number (20000 not 20k or 20,000)
- is_refinement = true only if modifying an existing plan
- Return ONLY the JSON
"""

    # First attempt
    try:
        raw = _call_llm(prompt, max_tokens=512)
        result = _parse_json_safe(raw)
        if result:
            return result
    except Exception:
        pass

    # Fallback attempt with simpler prompt
    try:
        fallback = f"""Extract from: "{user_input}"
Return ONLY this JSON with values filled in:
{{"destination": null, "days": null, "budget": null, "budget_currency": "INR", "mood": null, "constraints": [], "is_refinement": false}}"""
        raw = _call_llm(fallback, max_tokens=256)
        result = _parse_json_safe(raw)
        if result:
            return result
    except Exception:
        pass

    # Hard fallback
    return {
        "destination": None,
        "days": None,
        "budget": None,
        "budget_currency": "INR",
        "mood": "chill",
        "constraints": [],
        "is_refinement": False
    }


def generate_itinerary(destination: str, days: int, budget: float,
                       currency: str, mood: str, constraints: list) -> str:
    """Generate a full day-wise itinerary."""
    constraints_str = ", ".join(constraints) if constraints else "None"

    prompt = ITINERARY_GENERATION_PROMPT.format(
        destination=destination,
        days=days,
        budget=budget,
        currency=currency,
        mood=mood,
        constraints=constraints_str
    )

    try:
        return _call_llm(prompt, max_tokens=2048)
    except Exception as e:
        return f"Sorry, couldn't generate itinerary: {str(e)}"


def generate_budget_breakdown(destination: str, days: int,
                               budget: float, currency: str, mood: str) -> dict:
    """Generate budget breakdown — always sums exactly to budget."""

    keys = ["accommodation", "food", "transport", "activities", "miscellaneous"]
    b = int(budget)

    prompt = BUDGET_BREAKDOWN_PROMPT.format(
        destination=destination,
        days=days,
        budget=budget,
        currency=currency,
        mood=mood
    )

    try:
        raw = _call_llm(prompt, max_tokens=512)
        breakdown = _parse_json_safe(raw)

        if breakdown:
            # Force all to integers
            for k in keys:
                if k in breakdown:
                    breakdown[k] = int(float(breakdown.get(k, 0)))

            # Force exact sum = budget
            total = sum(breakdown.get(k, 0) for k in keys)
            if total > 0 and total != b:
                ratios = {k: breakdown.get(k, 0) / total for k in keys}
                for k in keys:
                    breakdown[k] = int(b * ratios[k])
                # Fix rounding gap → add remainder to accommodation
                new_total = sum(breakdown[k] for k in keys)
                breakdown["accommodation"] += b - new_total

            return breakdown

    except Exception:
        pass

    # Fallback: rule-based split that always sums correctly
    return {
        "accommodation": int(b * 0.40),
        "food": int(b * 0.25),
        "transport": int(b * 0.20),
        "activities": int(b * 0.10),
        "miscellaneous": b - int(b * 0.40) - int(b * 0.25) - int(b * 0.20) - int(b * 0.10),
        "tips": ["Book stays in advance", "Use local transport", "Eat at local dhabas"]
    }