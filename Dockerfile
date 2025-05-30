# Use a stable and minimal base image
FROM python:3.12-slim-bookworm

# Set environment variables to improve Docker behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Dash app code
COPY . .

# Expose the port
EXPOSE $PORT

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]
