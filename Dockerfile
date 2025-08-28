# Use lightweight Python image
FROM python:3.10-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port for Cloud Run
ENV PORT=8080

# Run app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
