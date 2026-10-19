import os
from pathlib import Path
from typing import List

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Read environment variables with safe defaults
HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "8000"))

# Database path (relative to BASE_DIR if not absolute)
raw_db_path = os.getenv("DATABASE_PATH", "data/dislikescope.db")
if os.path.isabs(raw_db_path):
    DATABASE_PATH = Path(raw_db_path)
else:
    DATABASE_PATH = BASE_DIR / raw_db_path

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# CORS Origins
raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ORIGINS: List[str] = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

# Limits
DEFAULT_SAMPLE_LIMIT: int = int(os.getenv("DEFAULT_SAMPLE_LIMIT", "100"))
MAX_SAMPLE_LIMIT: int = int(os.getenv("MAX_SAMPLE_LIMIT", "500"))
REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
