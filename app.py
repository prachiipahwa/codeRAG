import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(page_title="CodeRAG - Developer Assistant", page_icon="💻", layout="wide")

import os
from src.workspace_manager import WorkspaceManager
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface
from ui.debug_panel import render_debug_panel
from ui.evaluation_dashboard import render_evaluation_dashboard

# --- SESSION STATE INIT ---
if "projects" not in st.session_state:
    st.session_state.projects = WorkspaceManager.get_projects()
if "active_project" not in st.session_state:
    st.session_state.active_project = st.session_state.projects[0] if st.session_state.projects else None
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "debug_traces" not in st.session_state:
    st.session_state.debug_traces = {}

# Apply Developer Dark Theme
apply_theme()

# --- SIDEBAR ---
render_sidebar()

# --- MAIN LAYOUT (TABS) ---
tab_chat, tab_eval = st.tabs(["💬 Chat", "📊 Evaluate"])

with tab_chat:
    # Optional Debug Panel controls grid
    if st.session_state.debug_mode:
        # ChatGPT style layout: Main Chat Center, Debug Drawer Right
        col1, col2 = st.columns([2, 1])
        with col1:
            render_chat_interface()
        with col2:
            render_debug_panel()
    else:
        # Full width chat
        render_chat_interface()
        # Toggle hidden at bottom to enable debug mode if disabled
        st.write("")
        st.session_state.debug_mode = st.toggle("Enable Advanced Analytics Dashboard", value=st.session_state.debug_mode)
        if st.session_state.debug_mode:
            st.rerun()

with tab_eval:
    render_evaluation_dashboard()
