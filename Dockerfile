FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for FAISS and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security (Railway doesn't require this but it's good practice)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Railway automatically sets the PORT environment variable
# Your app should listen on 0.0.0.0:$PORT

# Command to run the application
CMD ["python", "start.py"]