FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/SEO_BOOSTER_2025 && chmod 777 /app/SEO_BOOSTER_2025

# Optional: extra safety for file limits
# RUN echo "* soft nofile 65535" >> /etc/security/limits.conf && \
#     echo "* hard nofile 65535" >> /etc/security/limits.conf

EXPOSE 5000

# Safe Gunicorn settings for your heavy bot
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
    "--workers", "1", \
    "--threads", "8", \
    "--timeout", "600", \
    "--max-requests", "100000", \
    "--max-requests-jitter", "5000", \
    "--log-level", "info", \
    "app:app"]