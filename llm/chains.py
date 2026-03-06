import json
import re
from groq import Groq
import os
from dotenv import load_dotenv
from llm.prompts import (
    INTENT_EXTRACTION_PROMPT,
    ITINERARY_GENERATION_PROMPT,
    BUDGET_BREAKDOWN_PROMPT,
    PACKING_LIST_PROMPT,
    WEATHER_ITINERARY_UPDATE_PROMPT,
    PERSONS_ITINERARY_UPDATE_PROMPT,
)

load_dotenv()

# ── Groq client ───────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def _call_llm(prompt: str, max_tokens: int = 2048) -> str:
    """Core LLM call — raises exception on failure."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _clean_json(raw: str) -> str:
    """Extract valid JSON block from LLM response."""
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)
    raw = raw.strip()
    start = raw.find("{")
    end   = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start:end + 1]
    return raw


def _parse_json_safe(raw: str) -> dict | None:
    """Try to parse JSON — return None on failure."""
    try:
        return json.loads(_clean_json(raw))
    except Exception:
        return None


# ── Intent Extraction ─────────────────────────────────────────

def extract_intent(user_input: str) -> dict:
    """Extract structured travel intent including persons + group_type."""

    prompt = INTENT_EXTRACTION_PROMPT.format(user_input=user_input)

    # First attempt
    try:
        raw    = _call_llm(prompt, max_tokens=512)
        result = _parse_json_safe(raw)
        if result:
            return result
    except Exception:
        pass

    # Fallback attempt
    try:
        fallback = f"""Extract from: "{user_input}"
Return ONLY this JSON with values filled in:
{{"destination": null, "days": null, "budget": null, "budget_currency": "INR",
  "mood": null, "constraints": [], "is_refinement": false,
  "persons": null, "group_type": null}}"""
        raw    = _call_llm(fallback, max_tokens=256)
        result = _parse_json_safe(raw)
        if result:
            return result
    except Exception:
        pass

    # Hard fallback
    return {
        "destination": None, "days": None, "budget": None,
        "budget_currency": "INR", "mood": "chill", "constraints": [],
        "is_refinement": False, "persons": 1, "group_type": "solo"
    }


# ── Itinerary Generation ──────────────────────────────────────

def generate_itinerary(
    destination: str,
    days: int,
    budget: float,
    currency: str,
    mood: str,
    constraints: list,
    persons: int = 1,
    group_type: str = "solo",
    weather_context: str = "Not specified",
) -> str:
    """Generate full day-wise itinerary with weather + group awareness."""

    per_person = int(budget / persons) if persons > 1 else int(budget)
    constraints_str = ", ".join(constraints) if constraints else "None"

    prompt = ITINERARY_GENERATION_PROMPT.format(
        destination=destination,
        days=days,
        budget=int(budget),
        currency=currency,
        mood=mood,
        persons=persons,
        group_type=group_type,
        per_person_budget=per_person,
        weather_context=weather_context,
        constraints=constraints_str,
    )

    try:
        return _call_llm(prompt, max_tokens=2048)
    except Exception as e:
        return f"Sorry, couldn't generate itinerary: {str(e)}"


# ── Budget Breakdown ──────────────────────────────────────────

def generate_budget_breakdown(
    destination: str,
    days: int,
    budget: float,
    currency: str,
    mood: str,
    persons: int = 1,
    group_type: str = "solo",
) -> dict:
    """Generate budget breakdown — always sums exactly to budget."""

    keys = ["accommodation", "food", "transport", "activities", "miscellaneous"]
    b    = int(budget)

    prompt = BUDGET_BREAKDOWN_PROMPT.format(
        destination=destination,
        days=days,
        budget=b,
        currency=currency,
        mood=mood,
        persons=persons,
        group_type=group_type,
    )

    try:
        raw       = _call_llm(prompt, max_tokens=512)
        breakdown = _parse_json_safe(raw)

        if breakdown:
            # Force integers
            for k in keys:
                if k in breakdown:
                    breakdown[k] = int(float(breakdown.get(k, 0)))

            # Force exact sum
            total = sum(breakdown.get(k, 0) for k in keys)
            if total > 0 and total != b:
                ratios = {k: breakdown.get(k, 0) / total for k in keys}
                for k in keys:
                    breakdown[k] = int(b * ratios[k])
                new_total = sum(breakdown[k] for k in keys)
                breakdown["accommodation"] += b - new_total

            return breakdown

    except Exception:
        pass

    # Fallback: rule-based
    return {
        "accommodation": int(b * 0.40),
        "food":          int(b * 0.25),
        "transport":     int(b * 0.20),
        "activities":    int(b * 0.10),
        "miscellaneous": b - int(b*0.40) - int(b*0.25) - int(b*0.20) - int(b*0.10),
        "tips": [
            "Book stays in advance",
            "Use local transport",
            "Eat at local restaurants"
        ]
    }


# ── Packing List ──────────────────────────────────────────────

def generate_packing_list(
    destination: str,
    days: int,
    mood: str,
    weather_context: str = "Not specified",
    persons: int = 1,
    group_type: str = "solo",
    constraints: list = [],
) -> dict:
    """Generate categorized packing list based on all trip context."""

    constraints_str = ", ".join(constraints) if constraints else "None"

    prompt = PACKING_LIST_PROMPT.format(
        destination=destination,
        days=days,
        mood=mood,
        weather_context=weather_context,
        persons=persons,
        group_type=group_type,
        constraints=constraints_str,
    )

    try:
        raw    = _call_llm(prompt, max_tokens=1024)
        result = _parse_json_safe(raw)
        if result:
            return result
    except Exception:
        pass

    # Fallback packing list
    return {
        "clothing":   ["Comfortable clothes", "Walking shoes", "Light jacket"],
        "toiletries": ["Toothbrush", "Toothpaste", "Shampoo", "Sunscreen"],
        "documents":  ["ID/Passport", "Flight/Train tickets", "Hotel booking", "Travel insurance"],
        "gadgets":    ["Phone charger", "Power bank", "Earphones"],
        "medical":    ["Basic first aid kit", "Personal medications", "Pain relievers"],
        "misc":       ["Reusable water bottle", "Snacks for travel", "Cash + cards"]
    }


# ── Weather-aware Itinerary Update ────────────────────────────

def update_itinerary_for_weather(
    current_itinerary: str,
    destination: str,
    days: int,
    budget: float,
    currency: str,
    mood: str,
    persons: int,
    weather_context: dict,
) -> str:
    """Update existing itinerary based on real weather data."""

    prompt = WEATHER_ITINERARY_UPDATE_PROMPT.format(
        current_itinerary=current_itinerary,
        destination=destination,
        days=days,
        budget=int(budget),
        currency=currency,
        mood=mood,
        persons=persons,
        travel_date=weather_context.get("date", "Not specified"),
        weather_desc=weather_context.get("desc", "Not specified"),
        weather_season=weather_context.get("season", "Not specified"),
        weather_emoji=weather_context.get("emoji", "🌤️"),
    )

    try:
        return _call_llm(prompt, max_tokens=2048)
    except Exception as e:
        return current_itinerary  # return unchanged on failure


# ── Persons-aware Itinerary Update ────────────────────────────

def update_itinerary_for_persons(
    current_itinerary: str,
    destination: str,
    days: int,
    budget: float,
    currency: str,
    mood: str,
    persons: int,
    group_type: str,
) -> str:
    """Update existing itinerary for new group size."""

    per_person = int(budget / persons) if persons > 1 else int(budget)

    prompt = PERSONS_ITINERARY_UPDATE_PROMPT.format(
        current_itinerary=current_itinerary,
        destination=destination,
        days=days,
        budget=int(budget),
        currency=currency,
        mood=mood,
        persons=persons,
        group_type=group_type,
        per_person_budget=per_person,
    )

    try:
        return _call_llm(prompt, max_tokens=2048)
    except Exception as e:
        return current_itinerary  # return unchanged on failure