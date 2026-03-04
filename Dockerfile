FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Expose port for HTTP wrapper
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the HTTP wrapper
CMD ["uvicorn", "http_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]
