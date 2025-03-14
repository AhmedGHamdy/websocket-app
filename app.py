import asyncio
import websockets
import json
import random

# List of stock tickers to simulate
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

async def stream_stock_data(websocket, path):
    while True:
        # Generate random stock prices for each ticker
        stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}
        await websocket.send(json.dumps(stock_data))
        await asyncio.sleep(1)

async def main():
    async with websockets.serve(stream_stock_data, "0.0.0.0", 8080):
        print("WebSocket server started on port 8080")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
