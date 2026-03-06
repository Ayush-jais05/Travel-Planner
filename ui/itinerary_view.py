import streamlit as st
from services.budget import format_currency
from utils.pdf_export import generate_pdf


def render_itinerary_panel():
    """Render the full right panel."""
    if not st.session_state.get("trip_active"):
        _render_empty_state()
        return

    _render_trip_header()
    st.markdown("---")
    _render_budget_breakdown()
    st.markdown("---")
    _render_itinerary()

    if st.session_state.get("packing_list"):
        st.markdown("---")
        _render_packing_list()

    st.markdown("---")
    _render_download_button()


# ── Empty State ───────────────────────────────────────────────

def _render_empty_state():
    st.markdown("""
    <div style='text-align:center; padding:4rem 2rem; color:#888;
                border:2px dashed #ddd; border-radius:12px; margin-top:2rem;'>
        <div style='font-size:3rem;'>🗺️</div>
        <h3 style='color:#aaa;'>Your itinerary will appear here</h3>
        <p>Start by telling the assistant your travel plans</p>
        <p style='font-size:0.85rem; color:#bbb;'>
            e.g. "3 days in Goa, ₹15k, chill vibe"
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Trip Header ───────────────────────────────────────────────

def _render_trip_header():
    destination   = st.session_state.get("destination", "Your Trip")
    days          = st.session_state.get("days", "")
    mood          = st.session_state.get("mood", "chill") or "chill"
    persons       = st.session_state.get("persons", 1) or 1
    group_type    = st.session_state.get("group_type", "solo") or "solo"
    currency      = st.session_state.get("current_currency", "INR")
    total         = st.session_state.get("total_budget", 0) or 0
    weather_desc  = st.session_state.get("weather_desc", "Not specified") or "Not specified"
    weather_emoji = st.session_state.get("weather_emoji", "🌤️") or "🌤️"
    travel_month  = st.session_state.get("travel_month")
    travel_season = st.session_state.get("travel_season")
    travel_date   = st.session_state.get("travel_date")

    mood_emojis = {
        "adventure": "🧗", "chill": "🌴", "romantic": "💑",
        "family": "👨‍👩‍👧", "culture": "🏛️"
    }
    group_emojis = {
        "solo": "🧍", "couple": "💑", "family": "👨‍👩‍👧", "group": "👥"
    }

    dest_emoji  = mood_emojis.get(mood, "✈️")
    group_emoji = group_emojis.get(group_type, "👥")

    st.markdown(f"## {dest_emoji} {destination}")

    # Row 1: Duration | Vibe | Budget
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Duration", f"{days} days")
    col2.metric("🎭 Vibe",     mood.capitalize())
    col3.metric("💰 Budget",   format_currency(total, currency))

    # Row 2: Travellers | Daily/Per Person | Weather
    col4, col5, col6 = st.columns(3)

    col4.metric(f"{group_emoji} Travellers", f"{persons} ({group_type.capitalize()})")

    # Fix: solo → show daily budget, group → show per person
    if persons > 1:
        per_person = st.session_state.get("per_person_budget") or int(total / persons)
        col5.metric("👤 Per Person", format_currency(per_person, currency))
    else:
        daily = int(total / days) if days and int(days) > 0 else 0
        col5.metric("📆 Per Day", format_currency(daily, currency))

    # Fix: weather label — short and clean
    if travel_date:
        weather_label = f"{weather_emoji} Weather"
        weather_val   = travel_date
    elif travel_season:
        weather_label = f"{weather_emoji} Season"
        weather_val   = travel_season
    elif travel_month:
        weather_label = f"{weather_emoji} Month"
        weather_val   = travel_month
    else:
        weather_label = "🌤️ Weather"
        weather_val   = "Add travel date!"

    col6.metric(weather_label, weather_val)

    # Weather detail banner — only if real weather set
    if weather_desc and weather_desc != "Not specified":
        st.info(f"{weather_emoji} **Weather:** {weather_desc}")


# ── Budget Breakdown ──────────────────────────────────────────

def _render_budget_breakdown():
    st.markdown("### 💸 Budget Breakdown")

    budget   = st.session_state.get("current_budget", {})
    currency = st.session_state.get("current_currency", "INR")
    total    = st.session_state.get("total_budget", 0) or 0
    persons  = st.session_state.get("persons", 1) or 1

    if not budget:
        st.info("Budget breakdown will appear after planning.")
        return

    categories = {
        "accommodation": ("🏨", "Accommodation"),
        "food":          ("🍽️", "Food"),
        "transport":     ("🚗", "Transport"),
        "activities":    ("🎯", "Activities"),
        "miscellaneous": ("💼", "Miscellaneous"),
    }

    for key, (emoji, label) in categories.items():
        amount = budget.get(key, 0)
        if not isinstance(amount, (int, float)):
            continue
        percent = (amount / total * 100) if total > 0 else 0

        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"{emoji} **{label}**")
        col2.markdown(f"**{format_currency(amount, currency)}**")

        if persons > 1:
            per_p = int(amount / persons)
            col3.markdown(f"*{format_currency(per_p, currency)}/person*")
        else:
            col3.markdown("")

        st.progress(min(percent / 100, 1.0))

    # Per person total — only for groups
    if persons > 1:
        per_person_total = int(total / persons)
        st.markdown(f"**👤 Per Person Total: {format_currency(per_person_total, currency)}**")

    # Budget tips
    tips = budget.get("tips", [])
    if tips:
        st.markdown("**💡 Budget Tips:**")
        for tip in tips:
            st.markdown(f"- {tip}")


# ── Itinerary ─────────────────────────────────────────────────

def _render_itinerary():
    st.markdown("### 📅 Your Itinerary")

    itinerary = st.session_state.get("current_itinerary", "")
    if not itinerary:
        st.info("Itinerary will appear here.")
        return

    st.markdown(itinerary)


# ── Packing List ──────────────────────────────────────────────

def _render_packing_list():
    st.markdown("### 🎒 Packing List")

    packing = st.session_state.get("packing_list", {})
    if not packing:
        return

    category_config = {
        "clothing":   ("👕", "Clothing"),
        "toiletries": ("🧴", "Toiletries"),
        "documents":  ("📄", "Documents"),
        "gadgets":    ("🔌", "Gadgets & Electronics"),
        "medical":    ("💊", "Medical & Health"),
        "misc":       ("🎒", "Miscellaneous"),
    }

    keys = list(category_config.keys())
    for i in range(0, len(keys), 2):
        col1, col2 = st.columns(2)

        key1   = keys[i]
        items1 = packing.get(key1, [])
        if items1:
            emoji1, label1 = category_config[key1]
            with col1:
                st.markdown(f"**{emoji1} {label1}**")
                for item in items1:
                    st.markdown(f"- {item}")

        if i + 1 < len(keys):
            key2   = keys[i + 1]
            items2 = packing.get(key2, [])
            if items2:
                emoji2, label2 = category_config[key2]
                with col2:
                    st.markdown(f"**{emoji2} {label2}**")
                    for item in items2:
                        st.markdown(f"- {item}")


# ── Download Buttons ──────────────────────────────────────────

def _render_download_button():
    destination = st.session_state.get("destination", "trip")

    col1, col2 = st.columns(2)

    # PDF download
    with col1:
        try:
            state = {
                "destination":       st.session_state.get("destination"),
                "days":              st.session_state.get("days"),
                "mood":              st.session_state.get("mood"),
                "total_budget":      st.session_state.get("total_budget"),
                "current_currency":  st.session_state.get("current_currency", "INR"),
                "persons":           st.session_state.get("persons", 1),
                "group_type":        st.session_state.get("group_type", "solo"),
                "per_person_budget": st.session_state.get("per_person_budget"),
                "weather_desc":      st.session_state.get("weather_desc", "Not specified"),
                "weather_emoji":     st.session_state.get("weather_emoji", ""),
                "travel_month":      st.session_state.get("travel_month"),
                "travel_season":     st.session_state.get("travel_season"),
                "travel_date":       st.session_state.get("travel_date"),
                "current_itinerary": st.session_state.get("current_itinerary"),
                "current_budget":    st.session_state.get("current_budget"),
                "packing_list":      st.session_state.get("packing_list"),
            }
            pdf_bytes = generate_pdf(state)
            st.download_button(
                label="⬇️ Download as PDF",
                data=pdf_bytes,
                file_name=f"{destination.replace(' ', '_')}_itinerary.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")

    # Text download
    with col2:
        itinerary = st.session_state.get("current_itinerary", "")
        packing   = st.session_state.get("packing_list", {})

        text_content = itinerary or ""
        if packing:
            text_content += "\n\n--- PACKING LIST ---\n"
            for cat, items in packing.items():
                text_content += f"\n{cat.upper()}:\n"
                for item in items:
                    text_content += f"  - {item}\n"

        st.download_button(
            label="📄 Download as Text",
            data=text_content,
            file_name=f"{destination.replace(' ', '_')}_itinerary.txt",
            mime="text/plain",
            use_container_width=True
        )