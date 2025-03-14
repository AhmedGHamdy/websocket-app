import asyncio
import websockets
import json
import random

# List of simulated stock tickers.
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

async def stream_stock_data(websocket, path=None):
    """
    WebSocket handler that streams simulated stock prices.
    If no path is provided, it defaults to None.
    """
    while True:
        # Create a dictionary of simulated stock prices.
        stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}
        # Send the stock data as JSON over the WebSocket.
        await websocket.send(json.dumps(stock_data))
        # Wait one second before sending the next update.
        await asyncio.sleep(1)

async def main():
    # Start the WebSocket server on 0.0.0.0:8080.
    async with websockets.serve(stream_stock_data, "0.0.0.0", 8080):
        print("WebSocket server started on port 8080")
        # Run forever.
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())