FROM python:3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential pkg-config libjpeg-dev zlib1g-dev libpng-dev libwebp-dev libtiff-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY scraper/pyproject.toml /app/pyproject.toml
COPY scraper/uv.lock /app/uv.lock

RUN uv sync --locked

COPY scraper /app/scraper

CMD ["uv", "run", "python", "scraper/main.py"]