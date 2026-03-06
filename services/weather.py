import requests
from datetime import datetime, timedelta
import re


# ── Season/month lookup (for when no real date is given) ──────
SEASON_WEATHER = {
    "January":   {"season": "Winter",       "desc": "Cold and dry, 5–15°C",          "emoji": "❄️"},
    "February":  {"season": "Winter",       "desc": "Cold, 8–18°C, pleasant",        "emoji": "❄️"},
    "March":     {"season": "Spring",       "desc": "Warm and pleasant, 15–25°C",    "emoji": "🌸"},
    "April":     {"season": "Spring",       "desc": "Warm, 18–28°C",                 "emoji": "🌸"},
    "May":       {"season": "Summer",       "desc": "Hot, 25–38°C",                  "emoji": "☀️"},
    "June":      {"season": "Monsoon",      "desc": "Rainy and humid, 25–32°C",      "emoji": "🌧️"},
    "July":      {"season": "Monsoon",      "desc": "Heavy rains, 24–30°C",          "emoji": "⛈️"},
    "August":    {"season": "Monsoon",      "desc": "Heavy rains, 24–30°C",          "emoji": "🌦️"},
    "September": {"season": "Post-Monsoon", "desc": "Mild rains clearing, 22–30°C",  "emoji": "🌤️"},
    "October":   {"season": "Autumn",       "desc": "Pleasant, 18–28°C",             "emoji": "🍂"},
    "November":  {"season": "Autumn",       "desc": "Cool and pleasant, 12–22°C",    "emoji": "🍂"},
    "December":  {"season": "Winter",       "desc": "Cold and dry, 8–18°C",          "emoji": "❄️"},
}

WEATHER_KEYWORDS = {
    "rainy":    {"season": "Monsoon", "desc": "Rainy weather expected",    "emoji": "🌧️"},
    "raining":  {"season": "Monsoon", "desc": "Rainy weather expected",    "emoji": "🌧️"},
    "rain":     {"season": "Monsoon", "desc": "Rainy weather expected",    "emoji": "🌧️"},
    "monsoon":  {"season": "Monsoon", "desc": "Monsoon season",            "emoji": "⛈️"},
    "snow":     {"season": "Winter",  "desc": "Snowy weather expected",    "emoji": "❄️"},
    "snowy":    {"season": "Winter",  "desc": "Snowy weather expected",    "emoji": "❄️"},
    "snowing":  {"season": "Winter",  "desc": "Snowing expected",          "emoji": "❄️"},
    "cold":     {"season": "Winter",  "desc": "Cold weather",              "emoji": "🧥"},
    "freezing": {"season": "Winter",  "desc": "Freezing weather",          "emoji": "🥶"},
    "hot":      {"season": "Summer",  "desc": "Hot weather",               "emoji": "🌡️"},
    "humid":    {"season": "Monsoon", "desc": "Humid weather",             "emoji": "💧"},
    "sunny":    {"season": "Summer",  "desc": "Sunny weather",             "emoji": "☀️"},
    "cloudy":   {"season": "Autumn",  "desc": "Cloudy weather",            "emoji": "☁️"},
    "overcast": {"season": "Autumn",  "desc": "Overcast skies",            "emoji": "☁️"},
    "summer":   {"season": "Summer",  "desc": "Summer season",             "emoji": "☀️"},
    "winter":   {"season": "Winter",  "desc": "Winter season",             "emoji": "❄️"},
    "spring":   {"season": "Spring",  "desc": "Spring season",             "emoji": "🌸"},
    "autumn":   {"season": "Autumn",  "desc": "Autumn season",             "emoji": "🍂"},
    "fall":     {"season": "Autumn",  "desc": "Fall season",               "emoji": "🍂"},
    "foggy":    {"season": "Winter",  "desc": "Foggy conditions",          "emoji": "🌫️"},
    "fog":      {"season": "Winter",  "desc": "Foggy conditions",          "emoji": "🌫️"},
    "storm":    {"season": "Monsoon", "desc": "Stormy weather expected",   "emoji": "⛈️"},
    "windy":    {"season": "Autumn",  "desc": "Windy conditions",          "emoji": "💨"},
}


def _get_coords(destination: str) -> tuple | None:
    """
    Get lat/lon for ANY city worldwide using Open-Meteo geocoding.
    No hardcoded list — works for Amsterdam, Paris, Tokyo, anything.
    """
    try:
        url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={destination}&count=1&language=en&format=json"
        )
        r = requests.get(url, timeout=6)
        data = r.json()
        if data.get("results"):
            result = data["results"][0]
            return (result["latitude"], result["longitude"])
    except Exception:
        pass
    return None


def _parse_relative_date(text: str) -> datetime | None:
    """Parse relative date mentions → actual datetime."""
    text_lower = text.lower()
    today = datetime.now()

    if "day after tomorrow" in text_lower:
        return today + timedelta(days=2)
    if "tomorrow" in text_lower:
        return today + timedelta(days=1)
    if "next week" in text_lower:
        return today + timedelta(weeks=1)
    if "next month" in text_lower:
        return (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    if "today" in text_lower or "tonight" in text_lower:
        return today
    if "this weekend" in text_lower:
        days_until_saturday = (5 - today.weekday()) % 7
        return today + timedelta(days=days_until_saturday)

    # "in X days"
    match = re.search(r"in\s+(\d+)\s+days?", text_lower)
    if match:
        return today + timedelta(days=int(match.group(1)))

    # "in X weeks"
    match = re.search(r"in\s+(\d+)\s+weeks?", text_lower)
    if match:
        return today + timedelta(weeks=int(match.group(1)))

    # "leaving on 15th" or "on March 15" or "on 15 March"
    match = re.search(
        r"(?:on\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-zA-Z]+)", text_lower
    )
    if match:
        try:
            day = int(match.group(1))
            month_str = match.group(2).capitalize()
            month_num = datetime.strptime(month_str, "%B").month
            year = today.year if month_num >= today.month else today.year + 1
            return datetime(year, month_num, day)
        except Exception:
            pass

    # "March 15" or "15 March"
    match = re.search(r"([a-zA-Z]+)\s+(\d{1,2})(?:st|nd|rd|th)?", text_lower)
    if match:
        try:
            month_str = match.group(1).capitalize()
            day = int(match.group(2))
            month_num = datetime.strptime(month_str, "%B").month
            year = today.year if month_num >= today.month else today.year + 1
            return datetime(year, month_num, day)
        except Exception:
            pass

    return None


def _parse_month_mention(text: str) -> str | None:
    """Extract month name from any text."""
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    text_lower = text.lower()
    for month in months:
        if month in text_lower:
            return month.capitalize()
    return None


def _parse_weather_keyword(text: str) -> dict | None:
    """Extract weather type from descriptive keywords."""
    text_lower = text.lower()
    for keyword, data in WEATHER_KEYWORDS.items():
        if keyword in text_lower:
            return data
    return None


def _weather_code_to_text(code: int) -> str:
    if code == 0:              return "Clear sky"
    elif code in [1, 2, 3]:   return "Partly cloudy"
    elif code in [45, 48]:    return "Foggy"
    elif code in [51, 53, 55]: return "Drizzle"
    elif code in [61, 63, 65]: return "Rainy"
    elif code in [71, 73, 75]: return "Snowy"
    elif code in [77]:         return "Snow grains"
    elif code in [80, 81, 82]: return "Rain showers"
    elif code in [85, 86]:     return "Snow showers"
    elif code in [95]:         return "Thunderstorm"
    elif code in [96, 99]:     return "Thunderstorm with hail"
    return "Variable"


def _weather_code_to_emoji(code: int) -> str:
    if code == 0:              return "☀️"
    elif code in [1, 2, 3]:   return "⛅"
    elif code in [45, 48]:    return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    elif code in [71, 73, 75, 77, 85, 86]: return "❄️"
    elif code in [95, 96, 99]: return "⛈️"
    return "🌤️"


def _temp_to_season(temp_max: float, precip: float) -> str:
    if precip > 5:      return "Monsoon"
    elif temp_max > 35: return "Summer"
    elif temp_max > 22: return "Spring"
    elif temp_max > 12: return "Autumn"
    return "Winter"


def fetch_real_weather(destination: str, date: datetime) -> dict | None:
    """
    Fetch real forecast from Open-Meteo for any city + date.
    Works for any city worldwide. No API key needed.
    """
    coords = _get_coords(destination)
    if not coords:
        return None

    lat, lon = coords
    date_str = date.strftime("%Y-%m-%d")
    today = datetime.now()
    days_ahead = max((date - today).days + 1, 1)
    forecast_days = min(days_ahead + 1, 16)  # Open-Meteo supports up to 16 days

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,"
            f"precipitation_sum,weathercode"
            f"&timezone=auto"
            f"&forecast_days={forecast_days}"
        )
        r = requests.get(url, timeout=8)
        data = r.json()
        daily = data.get("daily", {})
        dates = daily.get("time", [])

        # Find matching date
        idx = None
        if date_str in dates:
            idx = dates.index(date_str)
        elif dates:
            idx = 0  # use closest available

        if idx is not None:
            temp_max  = daily["temperature_2m_max"][idx]
            temp_min  = daily["temperature_2m_min"][idx]
            precip    = daily["precipitation_sum"][idx]
            code      = daily["weathercode"][idx]
            condition = _weather_code_to_text(code)
            emoji     = _weather_code_to_emoji(code)

            return {
                "source":        "api",
                "date":          date_str,
                "temp_max":      temp_max,
                "temp_min":      temp_min,
                "precipitation": precip,
                "condition":     condition,
                "emoji":         emoji,
                "desc":          f"{condition}, {temp_min:.0f}–{temp_max:.0f}°C",
                "season":        _temp_to_season(temp_max, precip),
            }

    except Exception:
        pass

    return None


def get_weather_context(user_input: str, destination: str) -> dict | None:
    """
    Master function — handles ALL weather input types:
    1. Relative dates: "tomorrow", "next week", "in 3 days", "on March 15"
    2. Month mentions: "December", "in January"
    3. Weather keywords: "rainy", "snowy", "hot", "monsoon"

    Works for ANY destination worldwide.
    Returns weather dict or None.
    """

    # Priority 1: Real date → fetch actual forecast
    date = _parse_relative_date(user_input)
    if date:
        weather = fetch_real_weather(destination, date)
        if weather:
            return weather
        # API failed → fall back to month estimate
        month = date.strftime("%B")
        season_data = SEASON_WEATHER.get(month, {})
        return {
            "source": "fallback",
            "date":   date.strftime("%Y-%m-%d"),
            "season": season_data.get("season", "Unknown"),
            "desc":   season_data.get("desc", "Weather estimate"),
            "emoji":  season_data.get("emoji", "🌤️"),
        }

    # Priority 2: Month name mentioned
    month = _parse_month_mention(user_input)
    if month:
        season_data = SEASON_WEATHER.get(month, {})
        return {
            "source": "month",
            "month":  month,
            "season": season_data.get("season", "Unknown"),
            "desc":   season_data.get("desc", "Seasonal estimate"),
            "emoji":  season_data.get("emoji", "🌤️"),
        }

    # Priority 3: Weather keyword mentioned
    weather_data = _parse_weather_keyword(user_input)
    if weather_data:
        return {
            "source": "user_stated",
            "season": weather_data.get("season", "Unknown"),
            "desc":   weather_data.get("desc", "As described"),
            "emoji":  weather_data.get("emoji", "🌤️"),
        }

    return None