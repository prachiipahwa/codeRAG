import os
import shutil
from typing import List
from src.config import PROJECTS_DIR
from src.logger import logger

class WorkspaceManager:
    """Manages creation, deletion, and paths for isolated user projects."""
    
    @staticmethod
    def get_projects() -> List[str]:
        """Returns a list of all existing projects."""
        if not os.path.exists(PROJECTS_DIR):
            return []
        return [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
        
    @staticmethod
    def create_project(project_name: str) -> bool:
        """Creates a new project workspace. Returns True if created, False if already exists."""
        project_path = os.path.join(PROJECTS_DIR, project_name)
        if os.path.exists(project_path):
            logger.warning(f"Project '{project_name}' already exists.")
            return False
            
        os.makedirs(project_path)
        os.makedirs(os.path.join(project_path, "vector_store"))
        logger.info(f"Created new workspace for project '{project_name}'.")
        return True
        
    @staticmethod
    def delete_project(project_name: str):
        """Deletes a project workspace and all its data."""
        project_path = os.path.join(PROJECTS_DIR, project_name)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
            logger.info(f"Deleted workspace for project '{project_name}'.")
            
    @staticmethod
    def rename_project(old_name: str, new_name: str) -> bool:
        """Renames a project workspace."""
        old_path = os.path.join(PROJECTS_DIR, old_name)
        new_path = os.path.join(PROJECTS_DIR, new_name)
        if not os.path.exists(old_path) or os.path.exists(new_path):
            return False
        os.rename(old_path, new_path)
        logger.info(f"Renamed workspace from '{old_name}' to '{new_name}'.")
        return True

    @staticmethod
    def get_project_stats(project_name: str) -> dict:
        """Returns statistics for a project workspace."""
        dirs = WorkspaceManager.get_project_dirs(project_name)
        stats = {
            "files_indexed": 0,
            "chunks_stored": 0, # Approximation or retrieved from vector store if needed
            "last_indexed": "Never"
        }
        
        if os.path.exists(dirs["cache"]):
            import json
            try:
                with open(dirs["cache"], "r") as f:
                    cache = json.load(f)
                    stats["files_indexed"] = len(cache)
            except:
                pass
                
        index_file = os.path.join(dirs["vector_store"], "index.faiss")
        if os.path.exists(index_file):
            import time
            from datetime import datetime
            mtime = os.path.getmtime(index_file)
            stats["last_indexed"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            # We don't easily know exact chunk count without loading faiss, leave 0 or generic
            
        return stats
        
    @staticmethod
    def get_repository_tree(project_name: str) -> dict:
        """Returns a nested dictionary representing the repository structure based on indexed files."""
        dirs = WorkspaceManager.get_project_dirs(project_name)
        tree = {}
        if os.path.exists(dirs["cache"]):
            import json
            try:
                with open(dirs["cache"], "r") as f:
                    cache = json.load(f)
                
                # Build tree from file paths
                for filepath in cache.keys():
                    # Filename logic: it's usually an absolute path or relative path depending on ingestion
                    # We'll just split by separator and build a dict tree
                    parts = filepath.replace('\\', '/').split('/')
                    # take the last 3 or 4 parts to avoid long prefix paths if absolute
                    if len(parts) > 4:
                        parts = ["..."] + parts[-3:]
                        
                    current_level = tree
                    for part in parts[:-1]:
                        if part not in current_level:
                            current_level[part] = {}
                        current_level = current_level[part]
                    current_level[parts[-1]] = "file"
            except:
                pass
        return tree

    @staticmethod
    def get_project_dirs(project_name: str) -> dict:
        """Returns standard paths required for a given project."""
        base = os.path.join(PROJECTS_DIR, project_name)
        return {
            "base": base,
            "vector_store": os.path.join(base, "vector_store"),
            "bm25_index": os.path.join(base, "bm25_index.pkl"),
            "chats_db": os.path.join(base, "chats.sqlite"),
            "repo_map": os.path.join(base, "repo_map.json"),
            "cache": os.path.join(base, "cache.json")
        }
