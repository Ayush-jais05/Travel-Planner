import streamlit as st
from services.chat_service import handle_user_message, clear_trip


def render_chat_panel():
    """Render the left chat panel."""

    st.markdown("### 💬 Chat with your Travel Assistant")
    st.markdown("---")

    # Example prompts (shown when no trip active)
    if not st.session_state.get("trip_active"):
        st.markdown("**✨ Try these:**")
        examples = [
            "3 days in Manali, ₹12k, adventure",
            "5 days Goa trip under ₹20k, chill vibe",
            "4 days Rajasthan, ₹25k, culture & history",
            "Weekend Coorg trip, ₹8k, romantic"
        ]
        cols = st.columns(2)
        for i, example in enumerate(examples):
            if cols[i % 2].button(example, key=f"example_{i}", use_container_width=True):
                with st.spinner("Planning your trip..."):
                    handle_user_message(example)
                st.rerun()

        st.markdown("---")

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #888;'>
                <div style='font-size: 2rem;'>✈️</div>
                <p>Tell me where you want to go!<br>
                <small>e.g. "3 days in Goa, ₹15k, chill vibe"</small></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your trip request or refine existing plan...")

    if user_input:
        with st.spinner("Thinking..."):
            handle_user_message(user_input)
        st.rerun()

    # Clear button
    if st.session_state.get("trip_active"):
        st.markdown("---")
        if st.button("🗑️ Plan New Trip", use_container_width=True):
            clear_trip()
            st.rerun()