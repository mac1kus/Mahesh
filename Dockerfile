# Use Python 3.11 with Debian (needed for GLPK)
FROM python:3.11-slim

# Install GLPK and cleanup
RUN apt-get update && apt-get install -y glpk-utils && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask/Gunicorn
EXPOSE 5000

# Start the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
