import streamlit as st
import os
from src.workspace_manager import WorkspaceManager

def _render_tree_node(name: str, node: dict, level: int = 0):
    """Recursively renders a file tree node using expanders or text depending on if it's a dir or file."""
    indent = "&nbsp;" * (level * 4)
    if isinstance(node, dict):
        # It's a directory
        # We can either use expander or just write it
        # Try to use a native markdown for now, or just plain text with indent
        for key in sorted(node.keys()):
            child = node[key]
            if isinstance(child, dict):
                # Directory
                with st.expander(f"📁 {key}"):
                    _render_tree_node(key, child, level)
            else:
                # File
                # We could make file clicked load in right pane, but for now just display
                st.caption(f"📄 {key}")
    else:
        st.caption(f"📄 {name}")

def render_repo_explorer(project_name: str):
    st.subheader("Repository Explorer")
    
    tree = WorkspaceManager.get_repository_tree(project_name)
    if not tree:
        st.info("No files indexed yet.")
        return
        
    with st.expander("📂 Project Root"):
        _render_tree_node("root", tree, level=1)
