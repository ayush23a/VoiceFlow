import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# AUDIO
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 1
ROLLING_BUFFER_SIZE = 3
QUEUE_MAXSIZE = 5

# STT
WHISPER_MODEL = "small"
COMPUTE_TYPE = "int8"
BEAM_SIZE = 1
LANGUAGE = "en"
VAD_FILTER = True

# STREAMING
TRANSCRIBE_INTERVAL = 2

# UI & PORTS (configurable via .env)
BUBBLE_PORT = int(os.getenv("BUBBLE_PORT", "65433"))
VOICEFLOW_PORT = int(os.getenv("VOICEFLOW_PORT", "65432"))

# GROQ LLM POST-PROCESSING
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT", "2.5"))  # 2 to 3 seconds timeout
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.0"))
GROQ_ENABLED = os.getenv("GROQ_ENABLED", "true").lower() in ("true", "1", "yes")
