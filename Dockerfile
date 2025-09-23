# HackReality Bot Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data backups

# Set proper permissions
RUN chmod +x main.py run_tests.py

# Create non-root user
RUN useradd -m -u 1000 hackreality && \
    chown -R hackreality:hackreality /app

# Switch to non-root user
USER hackreality

# Expose port (if needed for health checks)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('bot_database.db').execute('SELECT 1')" || exit 1

# Run the bot
CMD ["python", "main.py"]
