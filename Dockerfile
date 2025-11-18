# Use a stable and minimal base image
FROM containers.renci.org/helxplatform/uv-base:v0.0.1

# Set environment variables to improve Docker behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050 \
    UV_PYTHON=python3.12.5 \
    DASH_ENV=production

# Install system dependencies for building Python packages and WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libglib2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libfreetype6 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY . .
RUN uv venv
RUN uv sync --locked --no-dev

# Expose the port
EXPOSE $PORT

# Run the application with Gunicorn
CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8050", "app:app", "--timeout", "120"]