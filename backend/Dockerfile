FROM python:3.11-slim

WORKDIR /app

# Added ffmpeg for video processing capabilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Updated to use Render's dynamic $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}