"""
Configuration module for Agentic Workflow
Handles LMStudio endpoint configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for LMStudio and other services"""

    # LMStudio Configuration
    LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "https://lmstudio.subh-dev.xyz/v1")
    LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
    LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "local-model")

    # Optional OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    @classmethod
    def get_lmstudio_config(cls):
        """Returns LMStudio configuration as dict"""
        return {
            "base_url": cls.LMSTUDIO_BASE_URL,
            "api_key": cls.LMSTUDIO_API_KEY,
            "model": cls.LMSTUDIO_MODEL
        }

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.LMSTUDIO_BASE_URL:
            raise ValueError("LMSTUDIO_BASE_URL is required")
        print(f"✓ Configuration loaded")
        print(f"  LMStudio URL: {cls.LMSTUDIO_BASE_URL}")
        print(f"  Model: {cls.LMSTUDIO_MODEL}")
