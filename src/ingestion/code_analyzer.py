import os
import ast
from typing import Dict, List

class CodeAnalyzer:
    """Performs lightweight static analysis on codebase to generate a structural map."""

    @staticmethod
    def extract_python_structure(file_path: str) -> Dict:
        """Extracts classes, functions, and imports from a Python file."""
        structure = {"imports": [], "classes": [], "functions": []}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        structure["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        structure["imports"].append(node.module)
                elif isinstance(node, ast.ClassDef):
                    structure["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    structure["functions"].append(node.name)
                    
        except Exception as e:
            pass # Ignore parsing errors for non-standard or malformed code
            
        return structure

    @staticmethod
    def generate_repo_map(directory: str) -> str:
        """Creates a readable summary of the repository structure."""
        repo_data = {}
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    repo_data[rel_path] = CodeAnalyzer.extract_python_structure(file_path)
                elif file.endswith(('.js', '.ts', '.java', '.cpp', '.md')): # Just record presence
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    repo_data[rel_path] = {"type": "File recorded, deep AST analysis not supported"}
                    
        # Format into a readable string document
        map_content = "# Repository Structure and Modules Map\n\n"
        map_content += "This document outlines the file structure, classes, functions, and relationships within this project.\n\n"
        
        for filepath, data in repo_data.items():
            map_content += f"## `{filepath}`\n"
            if "imports" in data and data["imports"]:
                map_content += f"- **Dependencies/Imports:** {', '.join(data['imports'][:10])}\n"
            if "classes" in data and data["classes"]:
                map_content += f"- **Classes Defined:** {', '.join(data['classes'])}\n"
            if "functions" in data and data["functions"]:
                map_content += f"- **Functions Defined:** {', '.join(data['functions'])}\n"
            map_content += "\n"
            
        return map_content
