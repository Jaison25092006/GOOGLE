---
title: VoltEdge Support Agent
emoji: 🎧
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: Customer-facing support agent built with Google ADK + Gemini
---

# VoltEdge Support Agent

A customer-facing support agent built with the **Google Agent Development Kit
(ADK)** and **Gemini**, for the Google Cloud Gen AI Academy APAC (Cohort 3),
Track 1.

## What it does

Handles order status, shipping, and returns for a fictional electronics store,
using two function tools that Gemini calls on its own:

| Tool | Purpose |
|---|---|
| `get_order_status(order_id)` | Looks up status, carrier, tracking, ETA |
| `create_return_request(order_id, reason)` | Opens an RMA; refuses undelivered orders |

Try: `Where's my order VE-10231?` — the tracking number it returns exists only
in the source, so a real answer proves the tool executed.

## Architecture

```
main.py            -> mounts ADK's FastAPI app, binds $PORT
support_agent/
  __init__.py      -> makes the package discoverable by ADK
  agent.py         -> root_agent + the two function tools
Dockerfile         -> one image, runs on HF Spaces and Cloud Run
```

## Backends

`agent.py` is identical on both; only environment variables change.

| Environment | Backend | Config |
|---|---|---|
| Local (`adk web`) | AI Studio, free tier | `support_agent/.env` |
| HF Spaces | AI Studio, free tier | `GOOGLE_API_KEY` Space Secret |
| Cloud Run | Vertex AI via ADC | `GOOGLE_GENAI_USE_VERTEXAI=TRUE` env var |

## Run locally

```bash
py -3.12 -m venv .venv
.venv/Scripts/activate          # Windows
pip install -r requirements.txt
cp support_agent/.env.example support_agent/.env   # add your key
adk web
```

## Notes

- `gemini-2.5-flash` is retired for newly created API keys and returns
  `404 NOT_FOUND`. This project uses `gemini-3.6-flash`, overridable via
  `GOOGLE_GENAI_MODEL`.
- The ADK web UI is a development tool. It is exposed here to make the demo
  usable; it is not a production front end.
