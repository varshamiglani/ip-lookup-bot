# Use a slim Python base
FROM python:3.11-slim

# Avoid interactive tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive     PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# Create app user
RUN useradd -ms /bin/bash appuser

# Install system deps (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    ca-certificates     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy deps first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY bot.py ./

# Use non-root
USER appuser

# Bot token provided at runtime: TELEGRAM_TOKEN
CMD ["python", "bot.py"]
