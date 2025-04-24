FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV SQL_AGENT_URL=http://localhost:10000
ENV PORT=8000
ENV HOST=0.0.0.0
ENV FLASK_DEBUG=False

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "api.web"] 