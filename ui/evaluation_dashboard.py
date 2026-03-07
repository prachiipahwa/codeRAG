import streamlit as st
import os
import pandas as pd
from datetime import datetime
from src.workspace_manager import WorkspaceManager
from evaluation.metrics import StandardMetrics
from src.retrieval.hybrid_search import HybridRetriever

def render_evaluation_dashboard():
    st.header("📊 Evaluation Dashboard")
    st.write("Test the retrieval quality of the active workspace with standard metrics.")
    
    if not st.session_state.active_project:
        st.warning("Please select a valid project first.")
        return
        
    try:
        retriever = HybridRetriever(st.session_state.active_project)
    except FileNotFoundError:
        st.warning("Project index empty. Upload code first.")
        return

    # Create dummy testing ground
    test_query = st.text_input("Test Query:", "How is authentication handled in this project?")
    ground_truth = st.text_input("Expected File/Module (substring match allowed):", "auth")
    
    if st.button("Run Evaluation", type="primary"):
        with st.spinner("Running retrieval pipeline..."):
            docs, _ = retriever.retrieve(test_query)
            
            # Extract retrieved sources for comparison
            retrieved_sources = [doc.metadata.get("source", "") for doc in docs]
            
            # Simple simulation of true positive
            y_true = [1 if ground_truth.lower() in src.lower() else 0 for src in retrieved_sources]
            y_pred = [1] * len(retrieved_sources) # Assumes the system predicted these as relevant
            
            if not retrieved_sources:
                st.error("No documents retrieved.")
                return
                
            # If no ground truth matched, mock for error display
            if sum(y_true) == 0:
                y_true[0] = 1 # Fake ground truth to prevent division by zero in metrics class if needed
                st.warning("Ground truth file not found in top N. Result will be poor.")
                y_true = [0] * len(retrieved_sources)
                
            metrics = StandardMetrics()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                p_3 = metrics.precision_at_k(y_true, y_pred, k=3)
                st.metric("Precision@3", f"{p_3:.2f}")
                
            with col2:
                r_3 = metrics.recall_at_k(y_true, y_pred, k=3, total_relevant=max(1, sum(y_true)))
                st.metric("Recall@3", f"{r_3:.2f}")
                
            with col3:
                mrr = metrics.mrr([y_true])
                st.metric("MRR", f"{mrr:.2f}")
                
            st.divider()
            st.subheader("Retrieved Items vs Ground Truth")
            df = pd.DataFrame({
                "Source": [os.path.basename(src) for src in retrieved_sources],
                "Match": ["✅ Yes" if gt == 1 else "❌ No" for gt in y_true]
            })
            st.dataframe(df, use_container_width=True)
