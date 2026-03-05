def split_budget(budget: float, mood: str) -> dict:
    """Split budget based on mood/vibe."""
    
    splits = {
        "adventure": {
            "accommodation": 0.30,
            "food": 0.20,
            "transport": 0.25,
            "activities": 0.20,
            "miscellaneous": 0.05
        },
        "chill": {
            "accommodation": 0.45,
            "food": 0.25,
            "transport": 0.15,
            "activities": 0.10,
            "miscellaneous": 0.05
        },
        "romantic": {
            "accommodation": 0.45,
            "food": 0.30,
            "transport": 0.10,
            "activities": 0.10,
            "miscellaneous": 0.05
        },
        "family": {
            "accommodation": 0.35,
            "food": 0.30,
            "transport": 0.20,
            "activities": 0.10,
            "miscellaneous": 0.05
        },
        "culture": {
            "accommodation": 0.35,
            "food": 0.20,
            "transport": 0.15,
            "activities": 0.25,
            "miscellaneous": 0.05
        }
    }
    
    ratio = splits.get(mood, splits["chill"])
    
    return {
        "accommodation": round(budget * ratio["accommodation"]),
        "food": round(budget * ratio["food"]),
        "transport": round(budget * ratio["transport"]),
        "activities": round(budget * ratio["activities"]),
        "miscellaneous": round(budget * ratio["miscellaneous"]),
    }


def format_currency(amount: float, currency: str) -> str:
    """Format amount with currency symbol."""
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    symbol = symbols.get(currency, currency)
    
    if currency == "INR":
        # Indian formatting: 1,00,000
        if amount >= 100000:
            return f"{symbol}{amount/100000:.1f}L"
        elif amount >= 1000:
            return f"{symbol}{amount/1000:.1f}k"
        else:
            return f"{symbol}{int(amount)}"
    else:
        return f"{symbol}{amount:,.0f}"


def validate_budget(budget: float, days: int, currency: str) -> dict:
    """Check if budget is realistic and return warnings."""
    
    # Minimum daily budgets (very rough estimates)
    minimums = {
        "INR": 1500,   # ₹1500/day bare minimum in India
        "USD": 30,
        "EUR": 35,
        "GBP": 30
    }
    
    min_daily = minimums.get(currency, minimums["INR"])
    min_total = min_daily * days
    daily_budget = budget / days if days else budget
    
    if budget < min_total:
        return {
            "valid": False,
            "warning": f"Budget seems tight! Minimum recommended is {format_currency(min_total, currency)} for {days} days.",
            "daily": daily_budget
        }
    elif daily_budget > min_daily * 10:
        return {
            "valid": True,
            "warning": "Luxury budget detected — expect premium recommendations!",
            "daily": daily_budget
        }
    else:
        return {
            "valid": True,
            "warning": None,
            "daily": daily_budget
        }