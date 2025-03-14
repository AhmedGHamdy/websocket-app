import asyncio
import websockets
import json
import random
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Retrieve the Application Insights connection string
connection_string = os.getenv('APPINSIGHTS_CONNECTION_STRING')

# Print the connection string to verify it's being retrieved correctly (useful for debugging)
print(f"Connection String: {connection_string}")

# Check if the connection string is valid
if not connection_string:
    raise ValueError("Connection string is not set or is empty.")

# Set up Application Insights logging handler
logger = logging.getLogger(__name__)

# Configure the logger to write to the console as well
logging.basicConfig(level=logging.INFO)  # Ensures logs are output to console
logger.addHandler(AzureLogHandler(connection_string=connection_string))

# List of simulated stock tickers.
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

async def stream_stock_data(websocket, path=None):
    """
    WebSocket handler that streams simulated stock prices.
    If no path is provided, it defaults to None.
    """
    while True:
        try:
            # Create a dictionary of simulated stock prices.
            stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}

            # Log the stock data to Application Insights
            logger.info(f"Stock data: {json.dumps(stock_data)}")

            # Send the stock data as JSON over the WebSocket.
            await websocket.send(json.dumps(stock_data))

            # Wait one second before sending the next update.
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error occurred while streaming data: {e}")
            break  # In case of error, break the loop to prevent infinite retries

async def main():
    try:
        # Start the WebSocket server on 0.0.0.0:8080.
        async with websockets.serve(stream_stock_data, "0.0.0.0", 8080):
            print("WebSocket server started on port 8080")
            # Run forever.
            await asyncio.Future()  # Keeps the server running indefinitely
    except Exception as e:
        logger.error(f"WebSocket server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
