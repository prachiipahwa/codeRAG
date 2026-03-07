import logging
import os
import sys

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # We could also add a file handler here, but console is sufficient for dev UI
        # We'll rely on the Streamlit UI to present relevant debug info to the user
        
    return logger

# Global logger instance
logger = setup_logger("CodeRAG")