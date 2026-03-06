from llm.chains import (
    extract_intent,
    generate_itinerary,
    generate_budget_breakdown,
)
from services.budget import validate_budget, format_currency


def plan_trip(user_input: str) -> dict:
    """
    Main entry point for fresh trip planning.
    Extracts intent → validates → generates itinerary + budget.
    Returns full result dict.
    """

    # ── Step 1: Extract intent ────────────────────────────────
    intent = extract_intent(user_input)

    # ── Step 2: Validate required fields ─────────────────────
    missing = []
    if not intent.get("destination"):
        missing.append("destination")
    if not intent.get("days"):
        missing.append("number of days")
    if not intent.get("budget"):
        missing.append("budget")

    if missing:
        return {
            "success": False,
            "missing": missing,
            "message": (
                f"I need a few more details to plan your trip! "
                f"Please tell me your **{', '.join(missing)}**.\n\n"
                f"Example: *'3 days in Goa, ₹15k, chill vibe'*"
            ),
            "intent": intent
        }

    # ── Step 3: Parse values ──────────────────────────────────
    destination = intent["destination"]
    days        = int(intent["days"])
    budget      = float(intent["budget"])
    currency    = intent.get("budget_currency") or "INR"
    mood        = intent.get("mood") or "chill"
    constraints = intent.get("constraints") or []
    persons     = int(intent.get("persons") or 1)
    group_type  = intent.get("group_type") or _infer_group_type(persons, mood)

    # Ensure persons is at least 1
    if persons < 1:
        persons = 1

    per_person_budget = int(budget / persons)

    # ── Step 4: Validate budget ───────────────────────────────
    budget_check = validate_budget(budget, days, currency)

    # ── Step 5: Generate itinerary ────────────────────────────
    itinerary = generate_itinerary(
        destination     = destination,
        days            = days,
        budget          = budget,
        currency        = currency,
        mood            = mood,
        constraints     = constraints,
        persons         = persons,
        group_type      = group_type,
        weather_context = "Not specified yet — user can mention travel month or date",
    )

    # ── Step 6: Generate budget breakdown ─────────────────────
    breakdown = generate_budget_breakdown(
        destination = destination,
        days        = days,
        budget      = budget,
        currency    = currency,
        mood        = mood,
        persons     = persons,
        group_type  = group_type,
    )

    return {
        "success":          True,
        "intent":           intent,
        "itinerary":        itinerary,
        "budget":           breakdown,
        "raw_budget":       budget,
        "per_person_budget": per_person_budget,
        "budget_warning":   budget_check.get("warning"),
        "daily_budget":     format_currency(budget_check["daily"], currency),
        "total_budget":     format_currency(budget, currency),
        "currency":         currency,
        "destination":      destination,
        "days":             days,
        "mood":             mood,
        "constraints":      constraints,
        "persons":          persons,
        "group_type":       group_type,
    }


def _infer_group_type(persons: int, mood: str) -> str:
    """Infer group type from persons count + mood if not explicitly stated."""
    if persons == 1:
        return "solo"
    elif persons == 2 and mood == "romantic":
        return "couple"
    elif persons == 2:
        return "couple"
    elif persons <= 4 and mood == "family":
        return "family"
    elif persons >= 3:
        return "group"
    return "solo"