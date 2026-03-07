import os
import hashlib
import json
import zipfile
import shutil
import stat
from typing import List
from git import Repo
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.ingestion.vision_processor import VisionProcessor
from src.ingestion.code_analyzer import CodeAnalyzer
from src.workspace_manager import WorkspaceManager
from src.logger import logger

class DataIngestor:
    """Handles dynamic loading, hashing, and chunking of code, docs, images, zips, and git repos."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.dirs = WorkspaceManager.get_project_dirs(project_name)
        
        # Supported extensions
        self.code_extensions = {
            ".py": Language.PYTHON, ".js": Language.JS, 
            ".java": Language.JAVA, ".ts": Language.TS,
            ".cpp": Language.CPP, ".go": Language.GO
        }
        self.text_extensions = [".md", ".txt"]
        self.pdf_extensions = [".pdf"]
        self.image_extensions = [".png", ".jpg", ".jpeg"]
        
        # Tools
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", " ", ""]
        )
        self.vision_processor = VisionProcessor()
        
        # Document Hashing Cache
        self.cache_path = self.dirs["cache"]
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                return json.load(f)
        return {}
        
    def _save_cache(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def _hash_file(self, filepath: str) -> str:
        """Returns MD5 hash of a file's content."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def load_from_github(self, repo_url: str) -> List[Document]:
        """Clones a GitHub repo and processes its contents."""
        temp_dir = os.path.join(self.dirs["base"], "temp_repo")
        
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            
        logger.info(f"Cloning {repo_url} into {temp_dir}...")
        Repo.clone_from(repo_url, temp_dir)
        docs = self.process_directory(temp_dir)
        shutil.rmtree(temp_dir, onerror=remove_readonly)
        return docs

    def load_from_zip(self, zip_path: str) -> List[Document]:
        """Extracts a Zip file and processes its contents."""
        temp_dir = os.path.join(self.dirs["base"], "temp_zip")
        
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            
        logger.info(f"Extracting {zip_path} into {temp_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        docs = self.process_directory(temp_dir)
        shutil.rmtree(temp_dir, onerror=remove_readonly)
        return docs

    def process_directory(self, directory: str) -> List[Document]:
        """Processes all valid files in a directory."""
        all_docs = []
        files_to_process = []
        
        for root, dirs, files in os.walk(directory):
            # Block hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                files_to_process.append(os.path.join(root, file))
                
        # Generate and save Repo Map before individual processing
        repo_map_content = CodeAnalyzer.generate_repo_map(directory)
        with open(self.dirs["repo_map"], "w") as f:
            f.write(repo_map_content)
            
        # Add map to embedded documents
        map_doc = Document(
            page_content=repo_map_content, 
            metadata={"source": "repository_structural_map.json", "type": "repo_map"}
        )
        all_docs.extend(self.text_splitter.split_documents([map_doc]))

        # Process individual files
        for file_path in files_to_process:
            ext = os.path.splitext(file_path)[1].lower()
            
            # Skip unsupported
            if not any(ext in exts for exts in [self.code_extensions, self.text_extensions, self.pdf_extensions, self.image_extensions]):
                continue
                
            # Caching check
            file_hash = self._hash_file(file_path)
            if self.cache.get(file_path) == file_hash:
                logger.debug(f"Skipping cached file: {file_path}")
                continue # Skip unchanged
                
            logger.info(f"Processing new/modified file: {file_path}")
            
            if ext in self.code_extensions:
                all_docs.extend(self._process_code(file_path, ext))
            elif ext in self.text_extensions or ext in self.pdf_extensions:
                all_docs.extend(self._process_text(file_path, ext))
            elif ext in self.image_extensions:
                all_docs.extend(self._process_image(file_path))
                
            self.cache[file_path] = file_hash

        self._save_cache()
        return all_docs

    def _process_code(self, file_path: str, ext: str) -> List[Document]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=self.code_extensions[ext], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )
            return splitter.create_documents([content], metadatas=[{"source": os.path.basename(file_path), "type": "code"}])
        except Exception as e:
            logger.error(f"Failed to process code {file_path}: {e}")
            return []

    def _process_text(self, file_path: str, ext: str) -> List[Document]:
        try:
            if ext in self.text_extensions:
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                loader = PyPDFLoader(file_path)
                
            docs = loader.load()
            chunks = self.text_splitter.split_documents(docs)
            for c in chunks: 
                c.metadata["source"] = os.path.basename(file_path)
                c.metadata["type"] = "documentation"
            return chunks
        except Exception as e:
            logger.error(f"Failed to process text {file_path}: {e}")
            return []

    def _process_image(self, file_path: str) -> List[Document]:
        try:
            caption = self.vision_processor.generate_caption(file_path)
            doc = Document(
                page_content=f"Image Description of {os.path.basename(file_path)}:\n\n{caption}",
                metadata={"source": os.path.basename(file_path), "type": "diagram_caption"}
            )
            return self.text_splitter.split_documents([doc])
        except Exception as e:
            logger.error(f"Failed to process image {file_path}: {e}")
            return []
