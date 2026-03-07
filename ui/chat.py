import streamlit as st
import json
from src.chat_manager import ChatManager
from src.workspace_manager import WorkspaceManager
from src.retrieval.hybrid_search import HybridRetriever
from src.generation.chain import RAGChain
from src.logger import logger

def get_rag_chain():
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = RAGChain()
    return st.session_state.rag_chain

def render_chat_interface():
    # If no project or chat selected, show intro
    if not st.session_state.active_project:
        st.info("👈 Please create or select a project workspace on the left to begin.")
        return
    elif not st.session_state.active_chat_id:
        st.info("👈 Please select or create a New Chat on the left to begin typing.")
        return
        
    cm = ChatManager(st.session_state.active_project)
    history = cm.get_messages(st.session_state.active_chat_id)
    
    # Try to load retriever
    retriever = None
    try:
        retriever = HybridRetriever(st.session_state.active_project)
    except FileNotFoundError:
        st.warning("Project index empty. Upload code or enter a GitHub repo to enable RAG.")
        
    # --- Chat Header & Controls ---
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"💬 Active Chat ({st.session_state.active_project})")
    with col2:
        if st.button("🗑️ Clear", help="Clear chat messages"):
            cm.clear_chat(st.session_state.active_chat_id)
            st.rerun()

    # --- Render History ---
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Display source indicators for assistant
            if msg["role"] == "assistant" and msg.get("context"):
                with st.expander("Sources used"):
                    for i, doc in enumerate(msg["context"]):
                        st.caption(f"{i+1}. {doc.get('source', 'Unknown')}")
            
    # --- Input Handling ---
    if prompt := st.chat_input("Ask a question about your project..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        cm.add_message(st.session_state.active_chat_id, "user", prompt)
        
        with st.chat_message("assistant"):
            if not retriever:
                st.markdown("I cannot search this project yet. Please ingest data.")
            else:
                try:
                    with st.spinner("🔍 Analzying codebase and querying LLM..."):
                        start_time = st.session_state.get("__start__", 0) # Just rough timing
                        docs, traces = retriever.retrieve(prompt)
                        st.session_state.debug_traces = traces
                        
                        chain = get_rag_chain()
                        # We pass history directly as it's a list of dicts
                        answer = chain.generate(prompt, docs, chat_history=history)
                        
                        st.markdown(answer)
                        cm.add_message(st.session_state.active_chat_id, "assistant", answer, context=docs)
                        logger.info(f"Answered query: '{prompt}'")
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")
                    logger.error(f"Generation error: {str(e)}")
