import streamlit as st
from services.budget import format_currency


def render_itinerary_panel():
    """Render the right itinerary + budget panel."""

    if not st.session_state.get("trip_active"):
        _render_empty_state()
        return

    _render_trip_header()
    st.markdown("---")
    _render_budget_breakdown()
    st.markdown("---")
    _render_itinerary()


def _render_empty_state():
    """Show placeholder when no trip is planned."""
    st.markdown("""
    <div style='text-align: center; padding: 4rem 2rem; color: #888;
                border: 2px dashed #ddd; border-radius: 12px; margin-top: 2rem;'>
        <div style='font-size: 3rem;'>🗺️</div>
        <h3 style='color: #aaa;'>Your itinerary will appear here</h3>
        <p>Start by telling the assistant your travel plans</p>
    </div>
    """, unsafe_allow_html=True)


def _render_trip_header():
    """Render trip title and mood badge."""
    destination = st.session_state.get("destination", "Your Trip")
    days = st.session_state.get("days", "")
    mood = st.session_state.get("mood", "chill")

    mood_emojis = {
        "adventure": "🧗",
        "chill": "🌴",
        "romantic": "💑",
        "family": "👨‍👩‍👧",
        "culture": "🏛️"
    }
    emoji = mood_emojis.get(mood, "✈️")

    st.markdown(f"## {emoji} {destination}")

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Duration", f"{days} days")
    col2.metric("🎭 Vibe", mood.capitalize())

    currency = st.session_state.get("current_currency", "INR")
    budget = st.session_state.get("current_budget", {})
    total = st.session_state.get("total_budget") or sum(v for k, v in budget.items() if k != "tips" and isinstance(v, (int, float)))
    col3.metric("💰 Budget", format_currency(total, currency))

def _render_budget_breakdown():
    """Render budget breakdown as a visual bar."""
    st.markdown("### 💸 Budget Breakdown")

    budget = st.session_state.get("current_budget", {})
    currency = st.session_state.get("current_currency", "INR")

    if not budget:
        st.info("Budget breakdown will appear after planning.")
        return

    categories = {
        "accommodation": ("🏨", "Accommodation"),
        "food": ("🍽️", "Food"),
        "transport": ("🚗", "Transport"),
        "activities": ("🎯", "Activities"),
        "miscellaneous": ("💼", "Miscellaneous")
    }

    total = sum(
        v for k, v in budget.items()
        if k in categories and isinstance(v, (int, float))
    )

    for key, (emoji, label) in categories.items():
        amount = budget.get(key, 0)
        if not isinstance(amount, (int, float)):
            continue
        percent = (amount / total * 100) if total > 0 else 0

        col1, col2 = st.columns([3, 1])
        col1.markdown(f"{emoji} **{label}**")
        col2.markdown(f"**{format_currency(amount, currency)}**")
        st.progress(percent / 100)

    # Tips
    tips = budget.get("tips", [])
    if tips:
        st.markdown("**💡 Budget Tips:**")
        for tip in tips:
            st.markdown(f"- {tip}")


def _render_itinerary():
    """Render the full itinerary text."""
    st.markdown("### 📅 Your Itinerary")

    itinerary = st.session_state.get("current_itinerary", "")

    if not itinerary:
        st.info("Itinerary will appear here.")
        return

    st.markdown(itinerary)

    # Download button
    st.download_button(
        label="⬇️ Download Itinerary",
        data=itinerary,
        file_name=f"{st.session_state.get('destination', 'trip')}_itinerary.txt",
        mime="text/plain",
        use_container_width=True
    )