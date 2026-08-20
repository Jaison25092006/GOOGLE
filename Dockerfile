FROM python:3.12-slim

# Hugging Face Spaces runs containers as a NON-ROOT user (UID 1000), and only
# that user's home is reliably writable. Cloud Run does not care about the
# user, so this single image works for both targets -- no second Dockerfile.
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR $HOME/app

# requirements first so the pip layer caches: code edits rebuild in seconds
# instead of reinstalling every dependency.
COPY --chown=user requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=user . ./

# HF Spaces expects 7860 (declared as app_port in README.md frontmatter).
# Cloud Run injects PORT=8080 at runtime, which overrides the default below.
# Same image, both platforms, nothing hardcoded.
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
