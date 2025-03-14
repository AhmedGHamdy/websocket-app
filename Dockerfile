FROM python:3.9-slim

# Install pip (if not already installed)
RUN apt-get update && apt-get install -y python3-pip

WORKDIR /app

COPY app.py .

# Install required Python packages
RUN pip3 install --no-cache-dir opencensus websockets opencensus-ext-azure

EXPOSE 8080

CMD ["python", "app.py"]
