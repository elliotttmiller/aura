FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    torchaudio \
    diffusers \
    transformers \
    accelerate \
    flask \
    numpy \
    trimesh

# Copy server script
COPY main_server.py .

# Expose port
EXPOSE 5000

# Run server
CMD ["python", "main_server.py"]