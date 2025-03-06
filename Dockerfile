FROM python:3.14.0a4-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the dependencies file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the port your Dash app runs on
EXPOSE 8050

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]
