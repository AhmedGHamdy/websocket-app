FROM python:3.9-slim

WORKDIR /app

COPY app-local.py .

RUN pip3 install opencensus websockets opencensus-ext-azure

EXPOSE 8081
EXPOSE 8080

CMD ["python", "app-local.py"]
