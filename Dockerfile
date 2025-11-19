# STAGE 1: the build
FROM containers.renci.org/helxplatform/uv-base:v0.0.1 AS builder

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# copy dep files
COPY pyproject.toml uv.lock ./

# install deps
RUN uv venv && . .venv/bin/activate && uv sync --locked --no-dev

# copy in the application code
COPY . .


# stage 2: the final image
FROM python:3.12-slim

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050 \
    DASH_ENV=production

# install WeasyPrint runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libglib2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    shared-mime-info \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy the virtual environment from the builder stage
COPY --from=builder /app/.venv .venv

# copy the application code from the builder stage
COPY --from=builder /app .

# ensure the app is running with the venv python
ENV PATH="/app/.venv/bin:$PATH"

# expose the port
EXPOSE $PORT

# run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:app", "--timeout", "120"]