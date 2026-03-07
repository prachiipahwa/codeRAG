import streamlit as st
from src.config import UI_THEME

def apply_theme():
    """Applies the developer dark theme and custom CSS to Streamlit."""
    
    css = f"""
    <style>
    /* Base theme colors */
    :root {{
        --background: {UI_THEME['background']};
        --sidebar: {UI_THEME['sidebar']};
        --card: {UI_THEME['card']};
        --accent: {UI_THEME['accent']};
        --text: {UI_THEME['text']};
        --border: {UI_THEME['border']};
    }}
    
    /* App background */
    .stApp {{
        background-color: var(--background) !important;
        color: var(--text) !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar) !important;
        border-right: 1px solid var(--border);
    }}
    
    /* Top header area */
    header {{
        visibility: hidden;
    }}
    
    /* Reduce top padding */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}
    
    /* Chat message container styling */
    [data-testid="stChatMessage"] {{
        background-color: transparent;
        border: none;
    }}
    
    /* Assistant Chat bubbles */
    [data-testid="stChatMessage"][data-baseweb="layout"] > div > div:nth-child(2) {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    
    /* User Chat bubbles */
    [data-testid="stChatMessage"][data-baseweb="layout"]:has(div:contains("user")) > div > div:nth-child(2) {{
        background-color: var(--accent);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }}
    
    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    
    /* Code blocks */
    pre {{
        background-color: #0d1117 !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }}
    
    /* Input field */
    .stChatFloatingInputContainer {{
        background-color: transparent !important;
        border-top: none !important;
        padding-bottom: 20px;
    }}
    
    /* Chat input element itself */
    [data-testid="stChatInput"] {{
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        background-color: var(--card) !important;
    }}
    
    /* Divider */
    hr {{
        border-color: var(--border) !important;
    }}
    
    /* Buttons */
    div[data-testid="stButton"] button {{
        border-radius: 6px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--card) !important;
        color: var(--text) !important;
        transition: all 0.2s;
    }}
    div[data-testid="stButton"] button:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}
    
    /* Primary buttons */
    div[data-testid="stButton"] button[kind="primary"] {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: white !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: var(--card) !important;
        border-radius: 6px !important;
        border: 1px solid var(--border) !important;
    }}
    .streamlit-expanderContent {{
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-bottom-left-radius: 6px !important;
        border-bottom-right-radius: 6px !important;
    }}
    
    /* Tabs */
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
        color: #9ca3af !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
    }}
    
    /* Widget Overrides (Selectbox, Text Input, etc) */
    div[data-baseweb="select"] > div {{
        background-color: var(--card) !important;
        border-color: var(--border) !important;
    }}
    div[data-baseweb="input"] > div {{
        background-color: var(--card) !important;
        border-color: var(--border) !important;
    }}
    
    /* Change the default Streamlit pink/red primary color to our accent */
    .st-emotion-cache-1jicfl2 {{ 
        /* Toggles and checkboxes active state */
        background-color: var(--accent) !important;
    }}
    .st-emotion-cache-16idsys p {{
        /* Text inside primary buttons */
        color: white !important;
    }}
    
    /* Alerts / Status boxes */
    .stAlert {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    
    /* File Uploader */
    [data-testid="stFileUploadDropzone"] {{
        background-color: var(--card) !important;
        border: 1px dashed var(--border) !important;
    }}
    [data-testid="stFileUploadDropzone"]:hover {{
        border-color: var(--accent) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
