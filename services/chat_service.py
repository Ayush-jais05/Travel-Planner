import re
import json
import streamlit as st
from services.planner import plan_trip
from llm.chains import generate_budget_breakdown, _call_llm


def initialize_session():
    """Initialize all session state variables."""
    defaults = {
        "messages": [],
        "current_itinerary": None,
        "current_budget": None,
        "current_currency": "INR",
        "trip_active": False,
        "destination": None,
        "days": None,
        "mood": None,
        "total_budget": None,
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_message(role: str, content: str):
    """Add message to display history and LLM memory."""
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.chat_history.append({"role": role, "content": content})
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]


def _classify_intent(user_input: str) -> dict:
    """Use LLM to classify what the user wants."""
    prompt = f"""You are a classifier for a travel assistant app.
The user already has an active trip planned. Classify their message.

User message: "{user_input}"

Return ONLY a JSON object with no extra text:
{{
  "type": "modify_itinerary | budget_change | question | new_trip",
  "new_budget": number or null,
  "budget_operation": "set | add | reduce | null",
  "mood_change": "adventure | chill | romantic | family | culture | null"
}}

Rules:
- "new_trip" = completely different destination
- "modify_itinerary" = change activities, vibe, mood, days, add/remove places
- "budget_change" = changing/adding/reducing budget amount
- "question" = asking about hotels, food, tips, weather, packing, etc.
- new_budget = the NUMBER only (e.g. "30k" → 30000, "add 5k" → 5000)
- budget_operation: "set"=replace, "add"=add to current, "reduce"=subtract
"""
    try:
        raw = _call_llm(prompt, max_tokens=200)
        raw = re.sub(r"```json|```", "", raw).strip()
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            result = json.loads(raw[start:end+1])
            return result
    except Exception as e:
        print(f"=== CLASSIFY ERROR: {e} ===")

    # Fallback keyword classification
    text = user_input.lower()
    if any(w in text for w in ["budget", "cost", "money", "price", "spend", "expensive", "cheaper"]):
        return {"type": "budget_change", "new_budget": None, "budget_operation": "set", "mood_change": None}
    if any(w in text for w in ["change", "update", "modify", "make", "add", "remove", "vibe", "mood", "adventure", "chill", "romantic"]):
        return {"type": "modify_itinerary", "new_budget": None, "budget_operation": None, "mood_change": None}
    return {"type": "question", "new_budget": None, "budget_operation": None, "mood_change": None}


def _calculate_new_budget(intent: dict, current_budget: float) -> float | None:
    """Calculate final budget from intent + current budget."""
    raw_amount = intent.get("new_budget")
    operation = intent.get("budget_operation") or "set"

    if raw_amount is None:
        return None

    amount = float(raw_amount)

    if operation == "add":
        return current_budget + amount
    elif operation == "reduce":
        return max(current_budget - amount, 0)
    else:
        return amount


def _is_itinerary_response(text: str) -> bool:
    """Check if LLM response is a full itinerary."""
    indicators = [
        "Day 1", "Day 2", "### Day", "## 🗺️",
        "Morning:", "Afternoon:", "Evening:",
        "🌅 Morning", "☀️ Afternoon", "🌙 Evening",
        "**Morning", "**Afternoon", "**Evening",
        "**🌅", "**☀️", "**🌙"
    ]
    matches = sum(1 for ind in indicators if ind in text)
    return matches >= 2


def _build_context(user_input: str, instruction: str) -> str:
    """Build full context-aware prompt with trip memory + chat history."""
    history_lines = []
    for msg in st.session_state.chat_history[-10:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"][:300] + "..." if len(msg["content"]) > 300 else msg["content"]
        history_lines.append(f"{role}: {content}")
    history_text = "\n".join(history_lines) if history_lines else "No prior conversation."

    budget = st.session_state.current_budget or {}
    currency = st.session_state.current_currency

    return f"""You are a helpful travel assistant with full memory of this conversation.

═══ ACTIVE TRIP ═══
Destination: {st.session_state.destination}
Duration: {st.session_state.days} days
Total Budget: {st.session_state.total_budget} {currency}
Vibe/Mood: {st.session_state.mood}
Budget Breakdown:
  Accommodation: {budget.get('accommodation', 'N/A')} {currency}
  Food: {budget.get('food', 'N/A')} {currency}
  Transport: {budget.get('transport', 'N/A')} {currency}
  Activities: {budget.get('activities', 'N/A')} {currency}
  Miscellaneous: {budget.get('miscellaneous', 'N/A')} {currency}

Current Itinerary:
{st.session_state.current_itinerary}

═══ CONVERSATION HISTORY ═══
{history_text}

═══ USER SAYS ═══
{user_input}

═══ YOUR TASK ═══
{instruction}

Remember: Never ask the user to repeat their trip details. You have full context above.
"""


def handle_user_message(user_input: str) -> dict:
    """Main handler — LLM-powered with full memory and exception handling."""
    if not user_input or not user_input.strip():
        return {"success": False}

    add_message("user", user_input)

    try:
        currency = st.session_state.current_currency

        # ── Active trip ───────────────────────────────────────
        if st.session_state.trip_active and st.session_state.current_itinerary:

            intent = _classify_intent(user_input)
            intent_type = intent.get("type", "question")
            print(f"=== INTENT: {intent} ===")

            # ── New trip ──────────────────────────────────────
            if intent_type == "new_trip":
                st.session_state.trip_active = False
                st.session_state.current_itinerary = None
                st.session_state.current_budget = None
                st.session_state.chat_history = []
                # Fall through to plan fresh trip below

            # ── Budget change ─────────────────────────────────
            elif intent_type == "budget_change":
                new_budget = _calculate_new_budget(intent, st.session_state.total_budget or 0)

                if new_budget and new_budget > 0:
                    st.session_state.total_budget = new_budget
                    st.session_state.current_budget = generate_budget_breakdown(
                        destination=st.session_state.destination,
                        days=st.session_state.days,
                        budget=new_budget,
                        currency=currency,
                        mood=st.session_state.mood or "chill"
                    )

                    # Regenerate itinerary with new budget
                    response_text = _call_llm(_build_context(user_input,
                        f"Update the itinerary for the new budget of {new_budget} {currency}. "
                        f"Return ONLY the full itinerary in Day 1 / Day 2 format. No intro text."
                    ), max_tokens=2048)

                    if _is_itinerary_response(response_text):
                        st.session_state.current_itinerary = response_text

                    from services.budget import format_currency
                    reply = f"✅ Budget updated to **{format_currency(new_budget, currency)}**! Itinerary and breakdown refreshed →"
                else:
                    reply = "I couldn't figure out the new budget amount. Try saying '₹25k' or 'change budget to 30000'."

                add_message("assistant", reply)
                return {"success": True, "itinerary": st.session_state.current_itinerary,
                        "budget": st.session_state.current_budget}

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
                return {"success": True, "itinerary": st.session_state.current_itinerary,
                        "budget": st.session_state.current_budget}

            # ── Question / conversational ─────────────────────
            else:
                response_text = _call_llm(_build_context(user_input,
                    "Answer the user's question helpfully and conversationally using the trip context. "
                    "Be specific to their destination and budget. "
                    "Do NOT return an itinerary format — just a helpful answer."
                ), max_tokens=1024)

                add_message("assistant", response_text)
                return {"success": True, "itinerary": st.session_state.current_itinerary,
                        "budget": st.session_state.current_budget}

        # ── Fresh trip planning ───────────────────────────────
        result = plan_trip(user_input)

        if not result["success"]:
            add_message("assistant", result["message"])
            return result

        st.session_state.current_itinerary = result["itinerary"]
        st.session_state.current_budget = result["budget"]
        st.session_state.current_currency = result["currency"]
        st.session_state.trip_active = True
        st.session_state.destination = result["destination"]
        st.session_state.days = result["days"]
        st.session_state.mood = result["mood"]
        st.session_state.total_budget = result.get("raw_budget")

        msg = (
            f"🎉 Here's your **{result['days']}-day {result['destination']}** trip plan! "
            f"Total budget: **{result['total_budget']}** | Daily: **{result['daily_budget']}**"
        )
        if result.get("budget_warning"):
            msg += f"\n\n⚠️ {result['budget_warning']}"

        add_message("assistant", msg)
        return result

    except Exception as e:
        print(f"=== HANDLE MESSAGE ERROR: {e} ===")
        error_msg = "Something went wrong — please try again!"
        add_message("assistant", error_msg)
        return {"success": False, "error": str(e)}


def clear_trip():
    """Reset everything for a new trip."""
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.session_state.current_itinerary = None
    st.session_state.current_budget = None
    st.session_state.trip_active = False
    st.session_state.destination = None
    st.session_state.days = None
    st.session_state.mood = None
    st.session_state.total_budget = None