import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from src.workspace_manager import WorkspaceManager
from src.logger import logger

class ChatManager:
    """Handles multiple chat sessions per project using SQLite."""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db_path = WorkspaceManager.get_project_dirs(project_name)["chats_db"]
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                role TEXT,
                content TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (chat_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_chat(self, chat_id: str, name: str):
        """Creates a new chat session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO chats (chat_id, name) VALUES (?, ?)", (chat_id, name))
        conn.commit()
        conn.close()
        logger.info(f"Created chat session '{name}' ({chat_id}) in project '{self.project_name}'")

    def get_chats(self) -> List[Dict[str, str]]:
        """Returns all chat sessions for the active project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, name, created_at FROM chats ORDER BY created_at DESC")
        chats = [{"chat_id": row[0], "name": row[1], "created_at": row[2]} for row in cursor.fetchall()]
        conn.close()
        return chats

    def delete_chat(self, chat_id: str):
        """Deletes a given chat and its messages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        logger.info(f"Deleted chat session {chat_id}")

    def rename_chat(self, chat_id: str, new_name: str):
        """Renames a given chat session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE chats SET name = ? WHERE chat_id = ?", (new_name, chat_id))
        conn.commit()
        conn.close()

    def clear_chat(self, chat_id: str):
        """Clears all messages from a chat session without deleting the thread."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        logger.info(f"Cleared history for chat session {chat_id}")

    def add_message(self, chat_id: str, role: str, content: str, context: List[Any] = None):
        """Adds a message to the chat history. Context stores retrieved docs if role is assistant."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context_str = json.dumps([{"source": d.metadata.get("source"), "content": d.page_content} for d in context]) if context else None
        
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content, context) VALUES (?, ?, ?, ?)",
            (chat_id, role, content, context_str)
        )
        conn.commit()
        conn.close()

    def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Retrieves history for a chat session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, context, timestamp FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg = {"role": row[0], "content": row[1], "timestamp": row[3]}
            if row[2]:
                try:
                    msg["context"] = json.loads(row[2])
                except:
                    pass
            messages.append(msg)
        return messages
