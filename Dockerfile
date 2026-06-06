# Use Apify's Python base image
FROM apify/actor-python:3.12

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application and refinery core
COPY app/ ./app/
COPY src/ ./src/
# Force cache bust for refinery_core_src by using build arg
ARG REFINERY_VERSION=1.1.63-qa-deploy
RUN echo "Refinery version: $REFINERY_VERSION"
COPY refinery_core_src/ ./refinery_core_src/
RUN echo "Refinery core version: $(cat refinery_core_src/.version 2>/dev/null || echo 'unknown')"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Apify Actor
CMD ["python", "src/main.py"]