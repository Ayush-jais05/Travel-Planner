import re
import json
import streamlit as st
from services.planner import plan_trip
from services.weather import get_weather_context
from llm.chains import (
    _call_llm,
    generate_budget_breakdown,
    generate_packing_list,
    update_itinerary_for_weather,
    update_itinerary_for_persons,
)


# ── Session Initialization ────────────────────────────────────

def initialize_session():
    defaults = {
        # Core trip
        "messages":          [],
        "chat_history":      [],
        "current_itinerary": None,
        "current_budget":    None,
        "current_currency":  "INR",
        "trip_active":       False,
        "destination":       None,
        "days":              None,
        "mood":              None,
        "total_budget":      None,
        "constraints":       [],
        # Group
        "persons":           1,
        "group_type":        "solo",
        "per_person_budget": None,
        # Weather
        "travel_month":      None,
        "travel_season":     None,
        "weather_context":   None,
        "weather_desc":      "Not specified",
        "weather_emoji":     "🌤️",
        "travel_date":       None,
        # Packing
        "packing_list":      None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Message Helpers ───────────────────────────────────────────

def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.chat_history.append({"role": role, "content": content})
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]


# ── Intent Classification ─────────────────────────────────────

def _classify_intent(user_input: str) -> dict:
    """LLM-powered intent classifier for all message types."""

    prompt = f"""You are a classifier for a travel assistant app.
The user already has an active trip planned. Classify their message.

User message: "{user_input}"

Return ONLY a JSON object:
{{
  "type": "modify_itinerary | budget_change | weather_update | persons_update | packing_list | question | new_trip",
  "new_budget": number or null,
  "budget_operation": "set | add | reduce | null",
  "mood_change": "adventure | chill | romantic | family | culture | null",
  "persons": number or null,
  "group_type": "solo | couple | family | group | null"
}}

Classification rules:
- "new_trip"       = completely different destination requested
- "modify_itinerary" = change activities, vibe, mood, days, add/remove places
- "budget_change"  = changing / adding / reducing budget amount
- "weather_update" = mentions month, date, season, or weather condition
- "persons_update" = mentions group size, number of people, solo, couple, family
- "packing_list"   = asks about packing, what to carry, what to bring
- "question"       = hotels, food, tips, transport, anything else

For budget:
- new_budget = NUMBER only (30k → 30000, add 5k → 5000)
- budget_operation: "set"=replace total, "add"=add to current, "reduce"=subtract

For persons:
- "solo" / "alone" → 1
- "couple" / "me and partner" → 2
- "family of 4" → 4
- "me and 2 friends" → 3
- "group of 6" → 6

Return ONLY JSON, no explanation.
"""
    try:
        raw = _call_llm(prompt, max_tokens=256)
        raw = re.sub(r"```json|```", "", raw).strip()
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start:end+1])
    except Exception:
        pass

    # Keyword fallback
    text = user_input.lower()
    if any(w in text for w in ["pack", "carry", "bring", "luggage", "bag", "suitcase", "what to take"]):
        return {"type": "packing_list", "new_budget": None, "budget_operation": None, "mood_change": None, "persons": None, "group_type": None}
    if any(w in text for w in ["tomorrow", "next week", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "rainy", "sunny", "cold", "hot", "snow", "monsoon", "winter", "summer", "spring", "autumn"]):
        return {"type": "weather_update", "new_budget": None, "budget_operation": None, "mood_change": None, "persons": None, "group_type": None}
    if any(w in text for w in ["solo", "alone", "couple", "family", "group", "friends", "people", "persons", "travellers", "travelling with"]):
        return {"type": "persons_update", "new_budget": None, "budget_operation": None, "mood_change": None, "persons": None, "group_type": None}
    if any(w in text for w in ["budget", "cost", "money", "price", "spend", "expensive", "cheaper"]):
        return {"type": "budget_change", "new_budget": None, "budget_operation": "set", "mood_change": None, "persons": None, "group_type": None}
    if any(w in text for w in ["change", "update", "modify", "make", "add", "remove", "vibe", "mood"]):
        return {"type": "modify_itinerary", "new_budget": None, "budget_operation": None, "mood_change": None, "persons": None, "group_type": None}
    return {"type": "question", "new_budget": None, "budget_operation": None, "mood_change": None, "persons": None, "group_type": None}


# ── Budget Calculator ─────────────────────────────────────────

def _calculate_new_budget(intent: dict, current: float) -> float | None:
    amount    = intent.get("new_budget")
    operation = intent.get("budget_operation") or "set"
    if amount is None:
        return None
    amount = float(amount)
    if operation == "add":
        return current + amount
    elif operation == "reduce":
        return max(current - amount, 0)
    return amount


# ── Itinerary Response Detector ───────────────────────────────

def _is_itinerary_response(text: str) -> bool:
    indicators = [
        "Day 1", "Day 2", "### Day", "## 🗺️",
        "Morning:", "Afternoon:", "Evening:",
        "🌅 Morning", "☀️ Afternoon", "🌙 Evening",
        "**Morning", "**Afternoon", "**Evening",
        "**🌅", "**☀️", "**🌙"
    ]
    return sum(1 for i in indicators if i in text) >= 2


# ── Context Prompt Builder ────────────────────────────────────

def _build_context(user_input: str, instruction: str) -> str:
    history_lines = []
    for msg in st.session_state.chat_history[-10:]:
        role    = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"][:300] + "..." if len(msg["content"]) > 300 else msg["content"]
        history_lines.append(f"{role}: {content}")
    history_text = "\n".join(history_lines) or "No prior conversation."

    budget   = st.session_state.current_budget or {}
    currency = st.session_state.current_currency
    persons  = st.session_state.persons or 1
    per_person = int((st.session_state.total_budget or 0) / persons)

    return f"""You are a helpful travel assistant with full memory of this conversation.

═══ ACTIVE TRIP ═══
Destination:      {st.session_state.destination}
Duration:         {st.session_state.days} days
Total Budget:     {st.session_state.total_budget} {currency}
Per Person:       {per_person} {currency}
Vibe/Mood:        {st.session_state.mood}
Travellers:       {persons} person(s) — {st.session_state.group_type}
Weather/Season:   {st.session_state.weather_desc}

Budget Breakdown:
  Accommodation: {budget.get('accommodation', 'N/A')} {currency}
  Food:          {budget.get('food', 'N/A')} {currency}
  Transport:     {budget.get('transport', 'N/A')} {currency}
  Activities:    {budget.get('activities', 'N/A')} {currency}
  Miscellaneous: {budget.get('miscellaneous', 'N/A')} {currency}

Current Itinerary:
{st.session_state.current_itinerary}

═══ CONVERSATION HISTORY ═══
{history_text}

═══ USER SAYS ═══
{user_input}

═══ YOUR TASK ═══
{instruction}

Remember: Never ask the user to repeat trip details. You have full context above.
"""


# ── Main Handler ──────────────────────────────────────────────

def handle_user_message(user_input: str) -> dict:
    if not user_input or not user_input.strip():
        return {"success": False}

    add_message("user", user_input)

    try:
        currency = st.session_state.current_currency

        # ── Active trip ───────────────────────────────────────
        if st.session_state.trip_active and st.session_state.current_itinerary:

            intent      = _classify_intent(user_input)
            intent_type = intent.get("type", "question")

            # ── New trip ──────────────────────────────────────
            if intent_type == "new_trip":
                st.session_state.trip_active       = False
                st.session_state.current_itinerary = None
                st.session_state.current_budget    = None
                st.session_state.chat_history      = []
                st.session_state.packing_list      = None
                st.session_state.weather_context   = None
                st.session_state.weather_desc      = "Not specified"
                # fall through to plan fresh

            # ── Weather update ────────────────────────────────
            elif intent_type == "weather_update":
                weather = get_weather_context(user_input, st.session_state.destination)

                if weather:
                    # Save to session
                    st.session_state.weather_context = weather
                    st.session_state.weather_desc    = weather.get("desc", "Not specified")
                    st.session_state.weather_emoji   = weather.get("emoji", "🌤️")
                    st.session_state.travel_season   = weather.get("season")
                    if weather.get("month"):
                        st.session_state.travel_month = weather["month"]
                    if weather.get("date"):
                        st.session_state.travel_date  = weather["date"]

                    # Update itinerary for weather
                    updated = update_itinerary_for_weather(
                        current_itinerary = st.session_state.current_itinerary,
                        destination       = st.session_state.destination,
                        days              = st.session_state.days,
                        budget            = st.session_state.total_budget,
                        currency          = currency,
                        mood              = st.session_state.mood,
                        persons           = st.session_state.persons,
                        weather_context   = weather,
                    )
                    if _is_itinerary_response(updated):
                        st.session_state.current_itinerary = updated

                    emoji = weather.get("emoji", "🌤️")
                    desc  = weather.get("desc", "")
                    reply = f"{emoji} Got it! Weather context added: **{desc}**\nItinerary updated for these conditions → check the panel on the right."
                else:
                    reply = _call_llm(_build_context(user_input,
                        "Answer the user's weather/date question helpfully using the trip context."
                    ), max_tokens=512)

                add_message("assistant", reply)
                return {"success": True}

            # ── Persons update ────────────────────────────────
            elif intent_type == "persons_update":
                # Try intent JSON first, then LLM extraction
                new_persons    = intent.get("persons")
                new_group_type = intent.get("group_type")

                if not new_persons:
                    # Ask LLM to extract persons count
                    extract_prompt = f"""From this message, extract the number of travellers and group type.
Message: "{user_input}"
Return ONLY JSON: {{"persons": number, "group_type": "solo|couple|family|group"}}"""
                    try:
                        raw = _call_llm(extract_prompt, max_tokens=100)
                        data = json.loads(re.sub(r"```json|```", "", raw).strip())
                        new_persons    = data.get("persons", st.session_state.persons)
                        new_group_type = data.get("group_type", st.session_state.group_type)
                    except Exception:
                        new_persons    = st.session_state.persons
                        new_group_type = st.session_state.group_type

                new_persons    = int(new_persons) if new_persons else st.session_state.persons
                new_group_type = new_group_type or st.session_state.group_type

                # Update session
                st.session_state.persons           = new_persons
                st.session_state.group_type        = new_group_type
                st.session_state.per_person_budget = int((st.session_state.total_budget or 0) / new_persons)

                # Regenerate budget for group
                st.session_state.current_budget = generate_budget_breakdown(
                    destination = st.session_state.destination,
                    days        = st.session_state.days,
                    budget      = st.session_state.total_budget,
                    currency    = currency,
                    mood        = st.session_state.mood,
                    persons     = new_persons,
                    group_type  = new_group_type,
                )

                # Update itinerary for group
                updated = update_itinerary_for_persons(
                    current_itinerary = st.session_state.current_itinerary,
                    destination       = st.session_state.destination,
                    days              = st.session_state.days,
                    budget            = st.session_state.total_budget,
                    currency          = currency,
                    mood              = st.session_state.mood,
                    persons           = new_persons,
                    group_type        = new_group_type,
                )
                if _is_itinerary_response(updated):
                    st.session_state.current_itinerary = updated

                from services.budget import format_currency
                per_person_fmt = format_currency(st.session_state.per_person_budget, currency)
                reply = (
                    f"👥 Updated for **{new_persons} traveller(s)** ({new_group_type})! "
                    f"Per person budget: **{per_person_fmt}** → itinerary and breakdown refreshed."
                )
                add_message("assistant", reply)
                return {"success": True}

            # ── Budget change ─────────────────────────────────
            elif intent_type == "budget_change":
                new_budget = _calculate_new_budget(intent, st.session_state.total_budget or 0)

                if new_budget and new_budget > 0:
                    st.session_state.total_budget      = new_budget
                    st.session_state.per_person_budget = int(new_budget / (st.session_state.persons or 1))

                    st.session_state.current_budget = generate_budget_breakdown(
                        destination = st.session_state.destination,
                        days        = st.session_state.days,
                        budget      = new_budget,
                        currency    = currency,
                        mood        = st.session_state.mood,
                        persons     = st.session_state.persons,
                        group_type  = st.session_state.group_type,
                    )

                    # Regenerate itinerary with new budget
                    response_text = _call_llm(_build_context(user_input,
                        f"Update the itinerary for the new budget of {int(new_budget)} {currency}. "
                        f"Return ONLY the full itinerary in Day 1 / Day 2 format. No intro text."
                    ), max_tokens=2048)

                    if _is_itinerary_response(response_text):
                        st.session_state.current_itinerary = response_text

                    from services.budget import format_currency
                    reply = f"✅ Budget updated to **{format_currency(new_budget, currency)}**! Itinerary and breakdown refreshed →"
                else:
                    reply = "I couldn't figure out the new budget. Try '₹25k', 'add 5000', or 'reduce by 3k'."

                add_message("assistant", reply)
                return {"success": True}

            # ── Packing list ──────────────────────────────────
            elif intent_type == "packing_list":
                packing = generate_packing_list(
                    destination     = st.session_state.destination,
                    days            = st.session_state.days,
                    mood            = st.session_state.mood,
                    weather_context = st.session_state.weather_desc,
                    persons         = st.session_state.persons,
                    group_type      = st.session_state.group_type,
                    constraints     = st.session_state.constraints or [],
                )
                st.session_state.packing_list = packing
                reply = "🎒 Packing list generated! Check the panel on the right →"
                add_message("assistant", reply)
                return {"success": True}

            # ── Modify itinerary ──────────────────────────────
            elif intent_type == "modify_itinerary":
                mood_change = intent.get("mood_change")
                if mood_change:
                    st.session_state.mood = mood_change

                response_text = _call_llm(_build_context(user_input,
                    "Modify the itinerary as requested. Return ONLY the full updated itinerary "
                    "in Day 1 / Day 2 format. No intro text — start directly from Day 1."
                ), max_tokens=2048)

                if _is_itinerary_response(response_text):
                    st.session_state.current_itinerary = response_text
                    reply = "✅ Itinerary updated! Check the panel on the right →"
                else:
                    reply = response_text

                add_message("assistant", reply)
                return {"success": True}

            # ── General question ──────────────────────────────
            else:
                response_text = _call_llm(_build_context(user_input,
                    "Answer the user's question helpfully and conversationally. "
                    "Be specific to their destination, budget, group size and weather. "
                    "Do NOT return an itinerary format — just a helpful answer."
                ), max_tokens=1024)
                add_message("assistant", response_text)
                return {"success": True}

        # ── Fresh trip planning ───────────────────────────────
        result = plan_trip(user_input)

        if not result["success"]:
            add_message("assistant", result["message"])
            return result

        # Save everything
        st.session_state.current_itinerary = result["itinerary"]
        st.session_state.current_budget    = result["budget"]
        st.session_state.current_currency  = result["currency"]
        st.session_state.trip_active       = True
        st.session_state.destination       = result["destination"]
        st.session_state.days              = result["days"]
        st.session_state.mood              = result["mood"]
        st.session_state.total_budget      = result.get("raw_budget")
        st.session_state.persons           = result.get("persons", 1)
        st.session_state.group_type        = result.get("group_type", "solo")
        st.session_state.constraints       = result.get("constraints", [])
        st.session_state.per_person_budget = result.get("per_person_budget")
        st.session_state.packing_list      = None
        st.session_state.weather_context   = None
        st.session_state.weather_desc      = "Not specified"

        persons = st.session_state.persons or 1
        msg = (
            f"🎉 Here's your **{result['days']}-day {result['destination']}** trip plan! "
            f"Total: **{result['total_budget']}** | Daily: **{result['daily_budget']}**"
        )
        if persons > 1:
            from services.budget import format_currency
            per_p = format_currency(int((st.session_state.total_budget or 0) / persons), result["currency"])
            msg += f" | Per person: **{per_p}**"
        if result.get("budget_warning"):
            msg += f"\n\n⚠️ {result['budget_warning']}"
        msg += "\n\n💡 *You can tell me: travel month, group size, or ask for a packing list anytime!*"

        add_message("assistant", msg)
        return result

    except Exception as e:
        print(f"=== CHAT ERROR: {e} ===")
        add_message("assistant", "Something went wrong — please try again!")
        return {"success": False, "error": str(e)}


# ── Clear ─────────────────────────────────────────────────────

def clear_trip():
    keys = [
        "messages", "chat_history", "current_itinerary", "current_budget",
        "trip_active", "destination", "days", "mood", "total_budget",
        "constraints", "persons", "group_type", "per_person_budget",
        "travel_month", "travel_season", "weather_context", "weather_desc",
        "weather_emoji", "travel_date", "packing_list"
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    initialize_session()