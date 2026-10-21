# ---- SARPS web app: small, non-root, health-checked image ----
FROM python:3.12-slim
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv/sarps

# Install pinned dependencies first (better layer caching)
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --default-timeout=300 --retries=10 -r requirements.txt

# Copy only what the app needs (see .dockerignore)
COPY app/ app/
COPY sarps/ sarps/
COPY train_pipeline.py wsgi.py ./

# Train the model at build time so no model binary lives in Git
RUN mkdir -p models data && python train_pipeline.py > /dev/null

# Run as an unprivileged user
RUN useradd --system --uid 10001 --no-create-home sarps && chown -R sarps:sarps /srv/sarps
USER sarps

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status==200 else 1)"

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "wsgi:app"]
