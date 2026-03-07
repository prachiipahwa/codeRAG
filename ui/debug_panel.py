import streamlit as st
import os
from src.workspace_manager import WorkspaceManager
from src.chat_manager import ChatManager

def render_debug_panel():
    if not st.session_state.active_project:
        return
        
    tab1, tab2, tab3 = st.tabs(["Context Docs", "RAG Debug Trace", "Repo Map"])
    
    with tab1:
        st.subheader("Retrieved Context")
        if st.session_state.active_chat_id:
            cm = ChatManager(st.session_state.active_project)
            msgs = cm.get_messages(st.session_state.active_chat_id)
            latest_context = None
            for m in reversed(msgs):
                if m["role"] == "assistant" and "context" in m and m["context"]:
                    latest_context = m["context"]
                    break
            
            if latest_context:
                for i, doc in enumerate(latest_context):
                    source = doc.get("source", "Unknown") if isinstance(doc, dict) else (doc.metadata.get("source", "Unknown") if hasattr(doc, 'metadata') else "Unknown")
                    content = doc.get("content", "") if isinstance(doc, dict) else (doc.page_content if hasattr(doc, 'page_content') else str(doc))
                    
                    with st.expander(f"Top-{i+1}: {source}"):
                        st.code(content, language='python')
            else:
                st.write("No context retrieved for the latest turn.")
                
    with tab2:
        st.subheader("Retrieval Telemetry")
        if st.session_state.debug_traces:
            traces = st.session_state.debug_traces
            st.write("**Rewritten Queries (Multi-Query):**")
            for q in traces.get("multi_queries", []):
                st.caption(f"- {q}")
                
            with st.expander("HyDE Generated Document"):
                st.write(traces.get("hyde_document", ""))
                
            st.write("**Cross-Encoder Rerank Scores (Top 20):**")
            scores = traces.get("reranked_scores", [])
            for idx, s in enumerate(scores):
                color = "green" if s['score'] > 0.5 else ("orange" if s['score'] > 0.0 else "red")
                st.markdown(f"**{idx+1}. `{s['source']}`** - <span style='color:{color}'>{s['score']:.3f}</span>", unsafe_allow_html=True)
                with st.expander("Preview"):
                    st.write(s['content'])

    with tab3:
        st.subheader("Repository Structure map")
        map_path = WorkspaceManager.get_project_dirs(st.session_state.active_project)["repo_map"]
        if os.path.exists(map_path):
            with open(map_path, "r") as f:
                content = f.read()
            st.markdown(content)
        else:
            st.write("No codebase map generated yet.")
            
    # Fast toggle
    st.session_state.debug_mode = st.toggle("Enable Advanced Analytics Dashboard", value=st.session_state.get("debug_mode", False))
