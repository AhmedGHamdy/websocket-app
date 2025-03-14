FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip3 install opencensus websockets opencensus-ext-azure

EXPOSE 8080

CMD ["python", "app.py"]
