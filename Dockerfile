FROM python:3.10-slim

# Install system dependencies including ffmpeg and libsndfile for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set the PYTHONPATH so Python can find the backend modules
ENV PYTHONPATH=/app/backend

# Expose the port Render uses
EXPOSE 10000

# Start the application from the backend module
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--app-dir", "backend"]
