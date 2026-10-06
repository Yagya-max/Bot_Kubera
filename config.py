"""Configuration management for the local AI-driven trading bot prototype.

Defines Ollama API endpoints, watched ticker list, log paths, and timing constants.
"""

import os
from typing import List

# Ollama Settings
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GENERATE_URL: str = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Tickers to watch
WATCH_LIST: List[str] = ["XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD", "GBPUSD"]

# Execution Logging
LOG_FILE_PATH: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "paper_trades.log")
)

# Timing Constants (in seconds)
POLL_INTERVAL: int = 5
CONNECTION_TIMEOUT: int = 60

