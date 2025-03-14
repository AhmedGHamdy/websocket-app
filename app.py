import asyncio
import websockets
import json
import random
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from opencensus.stats import stats
from opencensus.stats import view
from opencensus.stats import aggregation
from opencensus.common import utils
from opencensus.ext.azure.metrics import MetricsExporter

# Set up Application Insights logging handler
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=YOUR_INSTRUMENTATION_KEY"))

# List of simulated stock tickers.
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

# Set up metrics collection
def init_metrics():
    view_manager = stats.stats.view_manager
    stats_recorder = stats.stats.stats_recorder
    exporter = MetricsExporter(connection_string="InstrumentationKey=YOUR_INSTRUMENTATION_KEY")
    
    # Define views (you can customize this part based on your needs)
    view.View(
        "stock_price",
        "Simulated stock prices",
        [],
        None,
        aggregation.Count()
    )
    
    # Register the view
    view_manager.register_view(view)
    
    # Start collecting data
    stats_recorder.new_measurement_map().measure_int("stock_price", 1).record()

# Function to stream stock data
async def stream_stock_data(websocket, path=None):
    """
    WebSocket handler that streams simulated stock prices.
    If no path is provided, it defaults to None.
    """
    while True:
        # Create a dictionary of simulated stock prices.
        stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}
        
        # Log the stock data to Application Insights (using logging).
        logger.info(f"Stock data: {json.dumps(stock_data)}")
        
        # Send the stock data as JSON over the WebSocket.
        await websocket.send(json.dumps(stock_data))
        
        # Wait one second before sending the next update.
        await asyncio.sleep(1)

async def main():
    # Initialize metrics and logging
    init_metrics()

    # Start the WebSocket server on 0.0.0.0:8080.
    async with websockets.serve(stream_stock_data, "0.0.0.0", 8080):
        print("WebSocket server started on port 8080")
        # Run forever.
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
