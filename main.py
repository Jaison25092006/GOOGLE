"""Container entrypoint. Serves the ADK web UI + API.

Runs unchanged on Hugging Face Spaces (port 7860, key from a Space Secret)
and on Cloud Run (port 8080, Vertex AI via ADC). Everything platform-specific
is read from the environment.
"""

import os
import sys

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# On HF Spaces there is no .env file -- config arrives as real environment
# variables from Space Secrets. setdefault means we supply a sane default
# WITHOUT clobbering anything the platform already set, so Cloud Run's
# GOOGLE_GENAI_USE_VERTEXAI=TRUE still wins.
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")

_USE_VERTEX = os.environ["GOOGLE_GENAI_USE_VERTEXAI"].strip().upper() in ("TRUE", "1")

# Fail loudly at startup instead of returning opaque 500s on the first chat
# message. On HF this is the difference between "Secret not set" in the build
# logs and ten minutes of guessing.
if not _USE_VERTEX and not os.environ.get("GOOGLE_API_KEY"):
    sys.exit(
        "FATAL: GOOGLE_API_KEY is not set and Vertex AI is disabled.\n"
        "  Hugging Face Spaces: Settings -> Variables and secrets -> "
        "new SECRET named GOOGLE_API_KEY.\n"
        "  Local: put it in support_agent/.env"
    )

print(
    f"[startup] backend={'Vertex AI' if _USE_VERTEX else 'AI Studio'} "
    f"model={os.environ.get('GOOGLE_GENAI_MODEL', 'gemini-3.6-flash (default)')} "
    f"port={os.environ.get('PORT', '7860 (default)')}",
    flush=True,
)

# Directory that CONTAINS agent packages -- not the package itself.
# This folder holds support_agent/, so ADK discovers it exactly as `adk web` does.
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    # Serve the dev chat UI as well as the API, so the Space URL is a
    # usable demo. ADK documents this UI as development-only.
    web=True,
    allow_origins=["*"],
)

if __name__ == "__main__":
    # HF Spaces: 7860. Cloud Run: injects PORT=8080. Never hardcode either.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
