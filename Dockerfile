# --- Build Stage ---
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .

# Change: Install to a neutral system directory instead of /root/.local
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Production Stage ---
FROM python:3.11-slim AS runner
WORKDIR /app

# Change: Copy from the neutral install path directly into the global site-packages area
COPY --from=builder /install /usr/local
COPY app.py .

ENV ENV=production
ENV PORT=8080

# DevOps Best Practice: Security (Don't run as root)
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# DevOps Best Practice: Container Health Check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Change: Hardcode the port string value since JSON array CMD blocks do not evaluate environment variables natively
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]