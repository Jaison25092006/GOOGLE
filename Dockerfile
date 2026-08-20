FROM python:3.12-slim

# Match the interpreter the agent was developed and tested against.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy requirements first so Docker caches the pip layer: code edits then
# rebuild in seconds instead of reinstalling every dependency.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Documentation only -- Cloud Run ignores EXPOSE and injects $PORT.
EXPOSE 8080

# Shell form so ${PORT} is expanded at runtime, not baked in at build time.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
