# Use a stable and minimal base image
FROM containers.renci.org/helxplatform/uv-base:v0.0.1

# Set environment variables to improve Docker behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050 \
    UV_PYTHON=python3.12.5

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY . .
RUN uv venv
RUN uv sync --locked --no-dev

# Expose the port
EXPOSE $PORT

# Run the application with Gunicorn
CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8050", "app:app"]
