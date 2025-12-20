import asyncio
import websockets
import json
import random

# List of simulated stock tickers.
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

async def stream_stock_data(websocket, path=None):
    """
    WebSocket handler that streams simulated stock prices.
    """
    while True:
        stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}
        await websocket.send(json.dumps(stock_data))
        await asyncio.sleep(1)

async def main():
    """
    Main coroutine to start both WebSocket servers on ports 8080 and 8081.
    """
    # Start both servers and manage their contexts
    async with websockets.serve(stream_stock_data, "0.0.0.0", 8080), \
               websockets.serve(stream_stock_data, "0.0.0.0", 8081):
        # Keep the servers running indefinitely
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())