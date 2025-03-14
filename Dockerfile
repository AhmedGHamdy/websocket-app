# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install dependencies
RUN pip install websockets opencensus-ext-azure aiohttp

# Copy application code
COPY app.py .

# Run the application
CMD ["python", "app.py"]