FROM python:3.10-slim

# Set environment variables
ENV MONGO_URI=mongodb://mongo:27017/
ENV FLASK_ENV=production
ENV PYTHONPATH=/home/app/src

WORKDIR /home/app

# Copy requirements and install dependencies
COPY setup.py /home/app/
COPY . /home/app/

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -e .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD [ "python", "./src/index.py" ]