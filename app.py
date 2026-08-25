"""
Streamlit demo UI for the Shopping Copilot foundation pipeline.

Run:
    streamlit run app.py

This is a thin UI layer only — all the actual logic (intent routing,
retrieval, ranking, state tracking) lives in agent.py and is untouched.
Useful for live demoing to judges / teammates without them reading code.
"""
import streamlit as st

from agent import ShoppingCopilotAgent
from data.sample_catalog import load_sample_catalog

st.set_page_config(page_title="Shopping Copilot — Prototype", page_icon="🛍️", layout="wide")

# --- session state setup ---------------------------------------------------
if "agent" not in st.session_state:
    st.session_state.agent = ShoppingCopilotAgent(load_sample_catalog())
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

agent = st.session_state.agent

# --- sidebar: live pipeline state -------------------------------------------
with st.sidebar:
    st.header("Pipeline state")
    state = agent.state_tracker.state
    st.metric("Turn", state.turn_count, help=f"Hard limit: 10")
    st.write("**Slots (accumulated):**")
    st.json(state.slots if state.slots else {"(none yet)": ""})
    st.caption(
        "Vector route = TF-IDF cosine (embedding stand-in). "
        "Ranking = hybrid score order (no LLM wired up yet)."
    )
    if st.button("Reset session"):
        st.session_state.agent = ShoppingCopilotAgent(load_sample_catalog())
        st.session_state.messages = []
        st.rerun()

st.title("🛍️ Shopping Copilot — Foundation Prototype")
st.caption("Dual-track intent routing + multi-route retrieval, running fully in-memory, no API key.")

# --- render chat history -----------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- handle new input ---------------------------------------------------------
user_text = st.chat_input("Try: \"looking for a gift\", \"under $30 in gold jewelry\", \"actually silver\"...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    resp = agent.handle_turn(user_text)

    with st.chat_message("assistant"):
        badge = "🛒 Buying" if resp.intent.value == "buying" else "🧭 Browsing"
        st.markdown(f"**Intent:** {badge}")

        if resp.action == "session_terminated":
            reply = "Session hit the 10-turn limit — please start a new session."
            st.warning(reply)

        elif resp.action == "clarify":
            reply = resp.clarification_prompt
            st.info(reply)

        else:  # results
            if not resp.results:
                reply = "No matches found for that yet — try loosening a constraint."
                st.warning(reply)
            else:
                lines = [f"Here's what I found ({len(resp.results)} shown):"]
                for r in resp.results:
                    p = agent.catalog_by_asin[r.asin]
                    price = f"${p.price:.2f}" if p.price is not None else "—"
                    lines.append(
                        f"- **{p.title}** ({p.asin}) — {price} — *{p.brand}* — score `{r.final_score:.3f}`"
                    )
                reply = "\n".join(lines)
                st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
