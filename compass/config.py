"""Central configuration. Values can be overridden with environment variables."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("COMPASS_DATA_DIR", ROOT / "var"))

# Two physically separate stores. The aggregation layer only ever opens SIGNALS_DB
# (read-only). Engineer feedback, dismissals and coaching history live in PRIVATE_DB.
SIGNALS_DB = DATA_DIR / "signals.db"
PRIVATE_DB = DATA_DIR / "private.db"
AUDIT_LOG = DATA_DIR / "access-audit.log"

WEB_DIR = ROOT / "web"
AGENT_KIT_DIR = ROOT / "agent-kit"
PROMPTS_JSON = AGENT_KIT_DIR / "prompt-library" / "prompts.json"
ANTI_PATTERNS_JSON = AGENT_KIT_DIR / "prompt-library" / "anti-patterns.json"
SAMPLE_JIRA_CSV = ROOT / "data" / "sample-jira-export.csv"

HOST = os.environ.get("COMPASS_HOST", "127.0.0.1")
PORT = int(os.environ.get("COMPASS_PORT", "8765"))

# Minimum group size before any team-level number is shown (k-anonymity).
K_ANON = int(os.environ.get("COMPASS_K_ANON", "5"))

# Synthetic data shape
WEEKS = 8
RANDOM_SEED = 20261015

# Session signing key is generated per process unless provided.
SECRET = os.environ.get("COMPASS_SECRET") or os.urandom(32).hex()

# Optional LLM enhancer. Off by default: the coach is fully deterministic and offline.
# Set COMPASS_LLM_URL to an approved OpenAI-compatible endpoint (for example a local
# model server) to let the prompt coach polish wording. Never required.
LLM_URL = os.environ.get("COMPASS_LLM_URL", "")
LLM_MODEL = os.environ.get("COMPASS_LLM_MODEL", "")
