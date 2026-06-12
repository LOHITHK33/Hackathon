import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("NEXUS_MODEL", "qwen2.5:7b")
HOST = os.environ.get("NEXUS_HOST", "127.0.0.1")
PORT = int(os.environ.get("NEXUS_PORT", "8000"))