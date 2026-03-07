import streamlit as st
import os
import uuid
from datetime import datetime
from src.workspace_manager import WorkspaceManager
from src.chat_manager import ChatManager
from src.ingestion.document_loaders import DataIngestor
from src.indexing.index_manager import IndexManager

def render_sidebar():
    from ui.repo_explorer import render_repo_explorer
    
    with st.sidebar:
        st.title("💻 CodeRAG")
        
        # --- WORKSPACE MANAGEMENT ---
        st.subheader("Workspaces")
        
        # Top level controls
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ New", use_container_width=True):
                st.session_state.show_create_workspace = not st.session_state.get("show_create_workspace", False)
                st.session_state.show_rename_workspace = False
        with col2:
            if st.button("✏️ Rename", use_container_width=True):
                st.session_state.show_rename_workspace = not st.session_state.get("show_rename_workspace", False)
                st.session_state.show_create_workspace = False
                
        # Handle Create
        if st.session_state.get("show_create_workspace", False):
            new_proj = st.text_input("New Workspace Name:")
            if st.button("Create", type="primary") and new_proj:
                if WorkspaceManager.create_project(new_proj):
                    st.session_state.projects = WorkspaceManager.get_projects()
                    st.session_state.active_project = new_proj
                    st.session_state.active_chat_id = None
                    st.session_state.show_create_workspace = False
                    st.success(f"Workspace '{new_proj}' created!")
                    st.rerun()
                else:
                    st.error("Workspace already exists.")
                    
        # Handle Rename
        if st.session_state.get("show_rename_workspace", False) and st.session_state.active_project:
            new_name = st.text_input("Rename Workspace To:", value=st.session_state.active_project)
            if st.button("Rename", type="primary") and new_name and new_name != st.session_state.active_project:
                if WorkspaceManager.rename_project(st.session_state.active_project, new_name):
                    st.session_state.projects = WorkspaceManager.get_projects()
                    st.session_state.active_project = new_name
                    st.session_state.show_rename_workspace = False
                    st.success(f"Renamed to {new_name}")
                    st.rerun()
                else:
                    st.error("Name taken or error occurred.")
        
        # Handle Select / Delete
        if st.session_state.projects:
            active_idx = st.session_state.projects.index(st.session_state.active_project) if st.session_state.active_project in st.session_state.projects else 0
            
            # Selector
            selected = st.selectbox("Active Workspace", st.session_state.projects, index=active_idx, label_visibility="collapsed")
            if selected != st.session_state.active_project:
                st.session_state.active_project = selected
                st.session_state.active_chat_id = None
                st.rerun()
                
            # Stats & Delete
            if st.session_state.active_project:
                stats = WorkspaceManager.get_project_stats(st.session_state.active_project)
                st.caption(f"📁 Files: {stats['files_indexed']} | ⏱️ {stats['last_indexed']}")
                
                # Expandable Delete
                with st.expander("Danger Zone"):
                    if st.button("🗑️ Delete Workspace", type="primary", use_container_width=True):
                        WorkspaceManager.delete_project(st.session_state.active_project)
                        st.session_state.projects = WorkspaceManager.get_projects()
                        st.session_state.active_project = st.session_state.projects[0] if st.session_state.projects else None
                        st.session_state.active_chat_id = None
                        st.toast("Workspace deleted.")
                        st.rerun()
                        
        # --- DATA INGESTION ---
        if st.session_state.active_project:
            st.divider()
            st.subheader("Data Ingestion")
            
            # GitHub Clone
            repo_url = st.text_input("GitHub URL:", placeholder="https://github.com/...")
            if st.button("Clone & Index repo", use_container_width=True) and repo_url:
                try:
                    with st.spinner("Cloning repository..."):
                        ingestor = DataIngestor(st.session_state.active_project)
                        docs = ingestor.load_from_github(repo_url)
                        if docs:
                            with st.spinner(f"Indexing {len(docs)} chunks..."):
                                manager = IndexManager(st.session_state.active_project)
                                manager.build_and_save(docs)
                                st.toast("✅ Indexed successfully!")
                        else:
                            st.toast("⚠️ No valid documents found.", icon="⚠️")
                except Exception as e:
                    st.error(f"Ingestion failed: {str(e)}")
                        
            # File Upload
            uploaded_files = st.file_uploader("Upload Files (Code/Zip)", accept_multiple_files=True, label_visibility="collapsed")
            if st.button("Process Uploads", use_container_width=True) and uploaded_files:
                try:
                    with st.spinner("Processing uploads..."):
                        base_dir = WorkspaceManager.get_project_dirs(st.session_state.active_project)["base"]
                        temp_dir = os.path.join(base_dir, "temp_uploads")
                        os.makedirs(temp_dir, exist_ok=True)
                        has_zip = False
                        
                        for f in uploaded_files:
                            path = os.path.join(temp_dir, f.name)
                            with open(path, "wb") as w:
                                w.write(f.read())
                            if f.name.endswith(".zip"):
                                has_zip = path
                                
                        ingestor = DataIngestor(st.session_state.active_project)
                        if has_zip:
                            docs = ingestor.load_from_zip(has_zip)
                        else:
                            docs = ingestor.process_directory(temp_dir)
                            
                        if docs:
                            with st.spinner(f"Indexing {len(docs)} chunks..."):
                                manager = IndexManager(st.session_state.active_project)
                                manager.build_and_save(docs)
                                st.toast("✅ Uploaded files indexed!")
                        else:
                            st.toast("⚠️ No valid documents found.", icon="⚠️")
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
                    
            # --- REPOSITORY EXPLORER ---
            st.divider()
            render_repo_explorer(st.session_state.active_project)
                    
            # --- CHAT SESSIONS ---
            st.divider()
            st.subheader("Chat Sessions")
            cm = ChatManager(st.session_state.active_project)
            
            if st.button("➕ New Chat", use_container_width=True):
                new_id = str(uuid.uuid4())
                cm.create_chat(new_id, f"Chat {datetime.now().strftime('%H:%M')}")
                st.session_state.active_chat_id = new_id
                st.rerun()
                
            chats = cm.get_chats()
            for c in chats:
                is_active = c['chat_id'] == st.session_state.active_chat_id
                
                # Use a container for edit controls
                container = st.container()
                col1, col2, col3 = container.columns([4, 1, 1])
                
                with col1:
                    btn_txt = f"🟢 {c['name']}" if is_active else c['name']
                    if st.button(btn_txt, key=f"chatbtn_{c['chat_id']}", use_container_width=True):
                        st.session_state.active_chat_id = c['chat_id']
                        st.session_state.edit_chat_id = None
                        st.rerun()
                
                with col2:
                    if st.button("✏️", key=f"edit_{c['chat_id']}", help="Rename"):
                        st.session_state.edit_chat_id = c['chat_id']
                        st.rerun()
                        
                with col3:
                    if st.button("🗑️", key=f"del_{c['chat_id']}", help="Delete"):
                        cm.delete_chat(c['chat_id'])
                        if st.session_state.active_chat_id == c['chat_id']:
                            st.session_state.active_chat_id = None
                        st.rerun()
                        
                # Rename logic
                if st.session_state.get("edit_chat_id") == c['chat_id']:
                    new_chat_name = st.text_input("New Name", value=c['name'], key=f"rename_{c['chat_id']}", label_visibility="collapsed")
                    if st.button("Save Name", key=f"save_{c['chat_id']}", type="primary", use_container_width=True):
                        cm.rename_chat(c['chat_id'], new_chat_name)
                        st.session_state.edit_chat_id = None
                        st.rerun()
