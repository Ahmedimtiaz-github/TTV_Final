# Dockerfile for TTV pipeline
# Uses only free/open-source tools: Python, ffmpeg, PIL, pyttsx3

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies needed
RUN pip install --no-cache-dir numpy

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY assets/ ./assets/
COPY run_demo.py .
COPY README.md .

# Set Python path
ENV PYTHONPATH=/app

# Default command: run demo
CMD ["python", "run_demo.py", "--demo", "--out", "demo_output.mp4"]
