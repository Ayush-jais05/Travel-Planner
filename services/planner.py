from llm.chains import (
    extract_intent,
    generate_itinerary,
    generate_budget_breakdown,
)
from services.budget import validate_budget, format_currency


def plan_trip(user_input: str) -> dict:
    """
    Main function: takes raw user input → returns full trip plan.
    """

    # Step 1: Extract intent
    intent = extract_intent(user_input)

    # Step 2: Validate required fields
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
            "message": f"Please tell me your {', '.join(missing)} to plan your trip!",
            "intent": intent
        }

    destination = intent["destination"]
    days = int(intent["days"])
    budget = float(intent["budget"])
    currency = intent.get("budget_currency", "INR")
    mood = intent.get("mood") or "chill"
    constraints = intent.get("constraints", [])

    # Step 3: Validate budget
    budget_check = validate_budget(budget, days, currency)

    # Step 4: Generate itinerary
    itinerary = generate_itinerary(
        destination=destination,
        days=days,
        budget=budget,
        currency=currency,
        mood=mood,
        constraints=constraints
    )

    # Step 5: Generate budget breakdown
    breakdown = generate_budget_breakdown(
        destination=destination,
        days=days,
        budget=budget,
        currency=currency,
        mood=mood
    )

    return {
        "success": True,
        "intent": intent,
        "itinerary": itinerary,
        "budget": breakdown,
        "raw_budget": budget,
        "budget_warning": budget_check.get("warning"),
        "daily_budget": format_currency(budget_check["daily"], currency),
        "total_budget": format_currency(budget, currency),
        "currency": currency,
        "destination": destination,
        "days": days,
        "mood": mood
    }