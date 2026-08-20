"""Cloud Run entrypoint.

`adk web` is a dev server. In a container we mount ADK's FastAPI app
ourselves so we control the port and CORS, and so Cloud Run's health
checks hit a real ASGI app.
"""

import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Directory that CONTAINS agent packages -- not the package itself.
# /app holds support_agent/, so ADK discovers it exactly as `adk web` does.
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    # Serve the dev chat UI as well as the API. Handy for demoing the
    # deployed agent; drop to web=False for a real production API.
    web=True,
    allow_origins=["*"],
)

if __name__ == "__main__":
    # Cloud Run injects PORT. Never hardcode 8080.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
