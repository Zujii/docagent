"""Hosted app: NEVER parses or runs a local LLM. Reads prebuilt chunks/embeddings; free API or replay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import streamlit as st  # noqa: E402

st.set_page_config(page_title="DocAgent", layout="wide")
st.title("DocAgent — cited research over your documents")

mode = st.sidebar.selectbox("Mode", ["Replay (always works)", "Hosted API (free tier)", "Local (Ollama + upload)"])
guardrails = st.sidebar.toggle("Guardrails", value=True)
use_critic = st.sidebar.toggle("Critic", value=True)

tab_ask, tab_evidence, tab_risk, tab_audit = st.tabs(["Ask", "Evidence", "Risk panel", "Audit trail"])

with tab_ask:
    q = st.text_input("Question about the indexed corpus")
    if st.button("Run") and q:
        # TODO: build provider by mode, call graph.invoke, store result in st.session_state
        st.info("Wire graph.invoke here (see cli.cmd_ask). In Replay mode, look up cached trace by question.")
    if mode.startswith("Local"):
        st.file_uploader("Upload PDFs (local mode only)", type="pdf", accept_multiple_files=True)

with tab_evidence:
    st.write("TODO: click a citation -> show page number + highlighted snippet.")
with tab_risk:
    st.write("TODO: table of RiskEvents; button to inject a test attack and show quarantine.")
with tab_audit:
    st.write("TODO: node-by-node timeline from the saved trace (latency, tokens, decisions).")
